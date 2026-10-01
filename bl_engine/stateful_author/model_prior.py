from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import re


class BehaviorOwner(str, Enum):
    USER='USER'; SOURCE_AUTHOR='SOURCE_AUTHOR'; CHARACTER='CHARACTER'; RELATIONSHIP='RELATIONSHIP'
    SCENE_FUNCTION='SCENE_FUNCTION'; PRESSURE_STATE='PRESSURE_STATE'; MODEL_DEFAULT='MODEL_DEFAULT'; UNKNOWN='UNKNOWN'


class ModelPriorStatus(str, Enum):
    SUSPECT='SUSPECT'; CONFIRMED='CONFIRMED'


@dataclass(frozen=True)
class BehaviorEvidence:
    behavior_family: str
    owner: BehaviorOwner
    evidence_refs: tuple[str,...]
    function: str
    confidence: float=1.0
    def __post_init__(self):
        object.__setattr__(self,'evidence_refs',tuple(self.evidence_refs))


@dataclass(frozen=True)
class ModelPriorFinding:
    family: str
    status: ModelPriorStatus
    evidence: tuple[str,...]=()


_LITERAL_FORMULAS=[
    re.compile(r'중요한 것은.{0,50}(?:이다|였다|다)'),
    re.compile(r'.{0,40}가 아니라.{0,50}(?:이다|였다|다)'),
    re.compile(r'(?:단순히|그저).{0,35}(?:아니|않).{0,50}(?:오히려|진짜|정말)'),
]
_MUTATED_FORMULAS=[
    re.compile(r'처음에는.{0,60}(?:줄 알았다|라고 생각했다|여겼다)'),
    re.compile(r'(?:남은 것은|남은 건|실제로 남은)'),
    re.compile(r'때문은 아니었'),
    re.compile(r'(?:라고 생각했다|라고 여겼다).{0,30}(?:틀렸다|아니었다)'),
]
_ABSTRACT_RESTATEMENT=re.compile(r'(?:그것|그건|이는|그 행동은).{0,35}(?:의미했|뜻했|배려였|증거였|표현이었)')
_CLOSURE_PATTERNS=[
    re.compile(x) for x in (
        r'(?:그 정도면|그것만으로|이 정도면).{0,10}(?:됐|충분)',
        r'더 바랄 (?:것|게)은? 없', r'(?:마음|가슴)이?\s*놓였', r'어깨.{0,12}힘이 빠졌',
        r'(?:이제|그래도).{0,8}괜찮', r'받아들일 수 있', r'조금은 알 것 같', r'이제야 알',
    )
]
_AFFECT_FAMILIES=(
    ('불안','초조','가라앉지','긴장'),
    ('두렵','무섭','겁','공포'),
    ('화가','분노','짜증','열받'),
    ('슬프','서럽','눈물','울고'),
)


def _owned(context:dict, family:str)->bool:
    for item in context.get('behavior_evidence',()):
        if not isinstance(item,BehaviorEvidence): continue
        if item.behavior_family != family: continue
        if item.owner in {BehaviorOwner.MODEL_DEFAULT,BehaviorOwner.UNKNOWN}: continue
        if not item.evidence_refs or item.confidence < .5: continue
        return True
    return False


def _clauses(text:str)->list[str]:
    return [x.strip() for x in re.split(r'[.!?。！？]+',text) if x.strip()]


def _semantic_echo(text:str)->bool:
    clauses=_clauses(text)
    for terms in _AFFECT_FAMILIES:
        hits=sum(any(term in clause for term in terms) for clause in clauses)
        if hits>=3: return True
    return False


def _closure_hits(text:str)->int:
    return sum(1 for p in _CLOSURE_PATTERNS if p.search(text))


def lexical_habit_quarantine(text:str, context:dict)->list[str]:
    recent=context.get('recent_texts',())
    if not recent: return []
    watch=('결국','문득','묘하게','이상하게','오히려','어쩐지')
    out=[]
    corpus='\n'.join([*map(str,recent),text])
    for token in watch:
        if corpus.count(token)>=4 and text.count(token)>=1 and not _owned(context,f'LEXICAL:{token}'):
            out.append(f'LEXICAL_HABIT:{token}')
    return out


def audit_model_prior_detailed(text:str, context:dict|None=None)->tuple[ModelPriorFinding,...]:
    context=context or {}; findings=[]
    literal=sum(bool(p.search(text)) for p in _LITERAL_FORMULAS)
    mutated=sum(bool(p.search(text)) for p in _MUTATED_FORMULAS)
    if literal>=2 or mutated>=2 or (literal>=1 and mutated>=1):
        findings.append(ModelPriorFinding('FORMULAIC_RHETORIC',ModelPriorStatus.CONFIRMED))
    clauses=_clauses(text)
    if len(clauses)>=3 and len(set(clauses)) <= max(1,len(clauses)//2) and not _owned(context,'REPETITION'):
        findings.append(ModelPriorFinding('FORMULAIC_REPETITION',ModelPriorStatus.CONFIRMED))
    if _ABSTRACT_RESTATEMENT.search(text) and not _owned(context,'ABSTRACT_RESTATEMENT'):
        findings.append(ModelPriorFinding('ABSTRACT_RESTATEMENT',ModelPriorStatus.CONFIRMED))
    if _semantic_echo(text) and not _owned(context,'SEMANTIC_ECHO'):
        findings.append(ModelPriorFinding('SEMANTIC_ECHO',ModelPriorStatus.CONFIRMED))
    closure_hits=_closure_hits(text)
    if closure_hits>=3:
        findings.append(ModelPriorFinding('AFFECTIVE_NORMALIZATION',ModelPriorStatus.CONFIRMED))
        findings.append(ModelPriorFinding('TERMINAL_CLOSURE_STACK',ModelPriorStatus.CONFIRMED))
    elif closure_hits and context.get('forbid_affective_normalization'):
        findings.append(ModelPriorFinding('AFFECTIVE_NORMALIZATION',ModelPriorStatus.CONFIRMED))
    elif closure_hits:
        findings.append(ModelPriorFinding('AFFECTIVE_NORMALIZATION',ModelPriorStatus.SUSPECT))
    for item in lexical_habit_quarantine(text,context):
        findings.append(ModelPriorFinding(item,ModelPriorStatus.CONFIRMED))
    return tuple(findings)


def audit_model_prior(text: str, context: dict | None = None) -> list[str]:
    return list(dict.fromkeys(f.family for f in audit_model_prior_detailed(text,context) if f.status is ModelPriorStatus.CONFIRMED))
