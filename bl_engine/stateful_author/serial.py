from __future__ import annotations
from dataclasses import dataclass, field, fields
import re


def _fs(v): return frozenset(v)

@dataclass(frozen=True)
class EpisodeDelta:
    fact_changes: frozenset[str] = field(default_factory=frozenset)
    belief_changes: frozenset[str] = field(default_factory=frozenset)
    relationship_changes: frozenset[str] = field(default_factory=frozenset)
    consequence_changes: frozenset[str] = field(default_factory=frozenset)
    commitment_changes: frozenset[str] = field(default_factory=frozenset)
    open_loop_changes: frozenset[str] = field(default_factory=frozenset)
    cliffhanger_only: bool = False
    metabolism: str | None = None

    def __post_init__(self):
        for name in ('fact_changes','belief_changes','relationship_changes','consequence_changes','commitment_changes','open_loop_changes'):
            object.__setattr__(self,name,frozenset(getattr(self,name)))

    def has_progress(self) -> bool:
        # Creating a dangling question is not progress by itself.
        return any((self.fact_changes,self.belief_changes,self.relationship_changes,self.consequence_changes,self.commitment_changes))

@dataclass(frozen=True)
class PressureVector:
    causal:int=0; information:int=0; relationship:int=0; desire:int=0; plan:int=0; identity:int=0; world:int=0; emotional_afterpressure:int=0
    def __post_init__(self):
        for f in fields(self):
            v=getattr(self,f.name)
            if not isinstance(v,int) or not 0 <= v <= 3:
                raise ValueError(f'PRESSURE_OUT_OF_RANGE:{f.name}')
    def active_dimensions(self)->set[str]:
        return {f.name for f in fields(self) if getattr(self,f.name)>0}


def _norm_question(s:str)->str:
    return re.sub(r'\s+',' ',s.strip()).casefold()

@dataclass(frozen=True)
class QuestionTransformation:
    old_question:str; partial_answer:str; reinterpretation:str; new_question:str; causal_link:bool; recoded_prior_evidence:bool
    evidence_refs: tuple[str,...]=()
    def is_valid(self)->bool:
        return bool(self.old_question.strip() and self.partial_answer.strip() and self.reinterpretation.strip() and self.new_question.strip() and self.causal_link and self.recoded_prior_evidence and _norm_question(self.old_question)!=_norm_question(self.new_question))

@dataclass(frozen=True)
class CharacterBehavioralPromise:
    stable_core:frozenset[str]; predictable_tendency:frozenset[str]; contradiction:frozenset[str]; violation_triggers:frozenset[str]
    def __post_init__(self):
        for n in ('stable_core','predictable_tendency','contradiction','violation_triggers'):
            object.__setattr__(self,n,frozenset(getattr(self,n)))


def evaluate_character_promise(promise:CharacterBehavioralPromise,*,action_tags:set[str],active_triggers:set[str])->list[str]:
    violations=[]
    for core in promise.stable_core:
        if core.startswith('protects_'):
            target=core[len('protects_'):]
            if any(tag in action_tags for tag in (f'abandons_{target}',f'betrays_{target}',f'kills_{target}',f'exposes_{target}')):
                violations.append(core)
    generic=any(tag.startswith('abandons_') or tag.startswith('betrays_') for tag in action_tags)
    if (violations or generic) and not (set(active_triggers)&set(promise.violation_triggers)):
        return ['UNMOTIVATED_PROMISE_BREAK']
    return []


def relationship_productive(data:dict)->bool:
    if not bool(data.get('evidence')): return False
    dims=('access_change','boundary_change','risk_change','attention_change','responsibility_change','labor_change','routine_change','distance_change','willingness_change','obligation_change','debt_change')
    return any(bool(data.get(k)) for k in dims)
