from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from .intelligence import SceneSignal, SignalSource


class CreativeSearchMode(str, Enum):
    COMBINE = 'COMBINE'
    EXPLORE = 'EXPLORE'
    REFRAME = 'REFRAME'
    TRANSFORM = 'TRANSFORM'


class SearchPath(str, Enum):
    DIRECT='DIRECT'
    LIGHT_EXPLORE='LIGHT_EXPLORE'
    HIGH_ASSURANCE='HIGH_ASSURANCE'


class AxiomClass(str, Enum):
    HARD_ANCHOR='HARD_ANCHOR'
    SOFT_CONSTRAINT='SOFT_CONSTRAINT'
    CHARACTER_ASSUMPTION='CHARACTER_ASSUMPTION'
    READER_ASSUMPTION='READER_ASSUMPTION'
    GENRE_DEFAULT='GENRE_DEFAULT'
    MODEL_DEFAULT='MODEL_DEFAULT'
    FREE_VARIABLE='FREE_VARIABLE'


class SceneMetabolism(str, Enum):
    TRANSFORM = 'TRANSFORM'
    CONSOLIDATE = 'CONSOLIDATE'
    INHABIT = 'INHABIT'
    RECOVER = 'RECOVER'
    CALIBRATE = 'CALIBRATE'
    INCUBATE = 'INCUBATE'
    RELEASE = 'RELEASE'


class ContradictionClass(str, Enum):
    CANON = 'CANON'
    KNOWLEDGE = 'KNOWLEDGE'
    BELIEF = 'BELIEF'
    SELF_MODEL_GAP = 'SELF_MODEL_GAP'
    GOAL_CONFLICT = 'GOAL_CONFLICT'
    VALUE_CONFLICT = 'VALUE_CONFLICT'
    RELATIONSHIP_PARADOX = 'RELATIONSHIP_PARADOX'
    READER_MODEL_COMPETITION = 'READER_MODEL_COMPETITION'
    TEMPORAL_CHANGE = 'TEMPORAL_CHANGE'
    VOICE_VARIATION = 'VOICE_VARIATION'


def classify_contradiction(name: str) -> ContradictionClass:
    key = name.strip().lower()
    mapping = {
        'canon': ContradictionClass.CANON,
        'knowledge': ContradictionClass.KNOWLEDGE,
        'belief': ContradictionClass.BELIEF,
        'self_model_gap': ContradictionClass.SELF_MODEL_GAP,
        'goal_conflict': ContradictionClass.GOAL_CONFLICT,
        'value_conflict': ContradictionClass.VALUE_CONFLICT,
        'relationship_paradox': ContradictionClass.RELATIONSHIP_PARADOX,
        'reader_model_competition': ContradictionClass.READER_MODEL_COMPETITION,
        'temporal_change': ContradictionClass.TEMPORAL_CHANGE,
        'voice_variation': ContradictionClass.VOICE_VARIATION,
    }
    if key not in mapping:
        raise ValueError(f'UNKNOWN_CONTRADICTION_CLASS:{name}')
    return mapping[key]


@dataclass(frozen=True)
class SceneDistinction:
    scene_id: str
    dominant_problem: str
    current_scene_function: SceneMetabolism
    consequence_level: str='LOW'
    knowledge_pressure: bool=False
    relationship_pressure: bool=False
    causal_pressure: bool=False
    strategic_pressure: bool=False
    affective_pressure: bool=False
    reader_uncertainty_pressure: bool=False
    major_reveal: bool=False
    irreversible_choice: bool=False
    relationship_phase_change: bool=False
    identity_sensitive: bool=False
    canon_sensitive: bool=False
    evidence_refs: tuple[str,...]=()
    unresolved_conflicts: tuple[str,...]=()


@dataclass(frozen=True)
class SearchDecision:
    path: SearchPath
    reason: str
    search_budget: int
    allowed_modes: tuple[CreativeSearchMode,...]


@dataclass(frozen=True)
class GenerativeAxiom:
    axiom_id: str
    proposition: str
    axiom_class: AxiomClass
    evidence_refs: tuple[str,...]=()
    transform_authority: bool=False
    def __post_init__(self):
        object.__setattr__(self,'evidence_refs',tuple(self.evidence_refs))


def authorize_transform(axiom: GenerativeAxiom) -> GenerativeAxiom:
    if axiom.axiom_class is AxiomClass.HARD_ANCHOR or not axiom.transform_authority:
        raise ValueError(f'AXIOM_TRANSFORM_FORBIDDEN:{axiom.axiom_id}')
    return axiom


@dataclass(frozen=True)
class CandidateGenealogy:
    changed_assumptions: tuple[str,...]
    preserved_assumptions: tuple[str,...]
    primary_changed_axis: str
    secondary_changed_axes: tuple[str,...]=()
    novelty_origin: str='UNKNOWN'
    grounding_dependencies: tuple[str,...]=()
    sibling_visibility: tuple[str,...]=()
    def __post_init__(self):
        object.__setattr__(self,'changed_assumptions',tuple(self.changed_assumptions))
        object.__setattr__(self,'preserved_assumptions',tuple(self.preserved_assumptions))
        object.__setattr__(self,'secondary_changed_axes',tuple(self.secondary_changed_axes))
        object.__setattr__(self,'grounding_dependencies',tuple(self.grounding_dependencies))
        object.__setattr__(self,'sibling_visibility',tuple(self.sibling_visibility))


@dataclass(frozen=True)
class CandidateConcept:
    candidate_id: str
    search_mode: CreativeSearchMode
    changed_assumptions: tuple[str, ...]
    causal_premise: str
    focal_interpretation: str
    knowledge_asymmetry: str
    option_change: str
    relationship_implication: str
    reader_effect: str
    creative_debts: tuple[str, ...] = ()
    genealogy: CandidateGenealogy | None = None
    goal_structure: str=''
    interaction_frame: str=''
    grounded_refs: tuple[str,...]=()
    def __post_init__(self):
        object.__setattr__(self,'changed_assumptions',tuple(self.changed_assumptions))
        object.__setattr__(self,'creative_debts',tuple(self.creative_debts))
        object.__setattr__(self,'grounded_refs',tuple(self.grounded_refs))


@dataclass(frozen=True)
class CrossExamRecord:
    candidate_id: str
    failures: tuple[str,...]=()
    grounded: bool=True
    authority_valid: bool=True
    locally_rational: bool=True
    causally_legible: bool=True
    reader_tractable: bool=True
    arbitrary: bool=False


@dataclass(frozen=True)
class SynthesizedConcept:
    winner_id: str
    causal_premise: str
    focal_interpretation: str
    knowledge_asymmetry: str
    option_change: str
    relationship_implication: str
    reader_effect: str
    contributions: tuple[str, ...] = ()


@dataclass(frozen=True)
class SearchReceipt:
    decision: SearchDecision
    candidates: tuple[CandidateConcept,...]=()
    cross_exam: tuple[CrossExamRecord,...]=()
    selected_conception: CandidateConcept | None=None
    candidate_texts: tuple[str,...]=()  # hard-empty: conception search never stores prose candidates
    status: str='NOT_REQUIRED'


def _grounded_true(value) -> tuple[bool, tuple[str,...]]:
    if not isinstance(value,SceneSignal) or not value.value:
        return False,()
    if value.source in {SignalSource.USER,SignalSource.STATE,SignalSource.TEXT_OBSERVED}:
        ok=value.confidence>=.5 and bool(value.evidence_refs)
    elif value.source is SignalSource.DERIVED:
        ok=value.confidence>=.8 and bool(value.evidence_refs)
    else:
        ok=False
    return ok,tuple(value.evidence_refs if ok else ())


def distinguish_scene(contract, scene_signals:dict, state:dict) -> SceneDistinction:
    evidence=[]
    flags={}
    for name in ('major_reveal','consequential_decision','relationship_pivot','high_pressure','mystery_evidence_conflict','strategic_ecology'):
        flags[name],refs=_grounded_true(scene_signals.get(name)); evidence.extend(refs)
    metabolism_raw=scene_signals.get('scene_metabolism')
    try:
        metabolism=SceneMetabolism(str(metabolism_raw)) if metabolism_raw else (SceneMetabolism.INHABIT if scene_signals.get('ordinary_domestic') else SceneMetabolism.TRANSFORM)
    except ValueError:
        metabolism=SceneMetabolism.TRANSFORM
    consequence='HIGH' if flags['major_reveal'] or flags['consequential_decision'] or flags['relationship_pivot'] else 'MEDIUM' if flags['high_pressure'] else 'LOW'
    return SceneDistinction(
        scene_id=contract.scene_id, dominant_problem=contract.requested_action, current_scene_function=metabolism,
        consequence_level=consequence, knowledge_pressure=flags['major_reveal'] or flags['mystery_evidence_conflict'],
        relationship_pressure=flags['relationship_pivot'], causal_pressure=flags['major_reveal'] or flags['consequential_decision'],
        strategic_pressure=flags['strategic_ecology'], affective_pressure=flags['high_pressure'],
        reader_uncertainty_pressure=flags['mystery_evidence_conflict'], major_reveal=flags['major_reveal'],
        irreversible_choice=flags['consequential_decision'], relationship_phase_change=flags['relationship_pivot'],
        canon_sensitive=bool(contract.locked_canon_refs) and consequence=='HIGH', evidence_refs=tuple(dict.fromkeys(evidence)),
    )


def decide_search(contract, distinction:SceneDistinction) -> SearchDecision:
    high=distinction.major_reveal or distinction.irreversible_choice or distinction.relationship_phase_change or distinction.canon_sensitive
    if high:
        return SearchDecision(SearchPath.HIGH_ASSURANCE,'high-consequence grounded scene distinction',3,
                              (CreativeSearchMode.EXPLORE,CreativeSearchMode.REFRAME,CreativeSearchMode.TRANSFORM))
    if contract.creative_freedom=='OPEN':
        return SearchDecision(SearchPath.LIGHT_EXPLORE,'explicitly open creative-freedom scope',2,(CreativeSearchMode.COMBINE,CreativeSearchMode.EXPLORE,CreativeSearchMode.REFRAME))
    return SearchDecision(SearchPath.DIRECT,'no high-cost creative search trigger',0,())


def structural_signature(c: CandidateConcept) -> tuple[str, ...]:
    if c.genealogy is not None:
        return (
            'AXIS:'+c.genealogy.primary_changed_axis.strip().upper(),
            'CHANGED:'+','.join(sorted(x.strip().lower() for x in c.genealogy.changed_assumptions)),
            'PRESERVED:'+','.join(sorted(x.strip().lower() for x in c.genealogy.preserved_assumptions)),
            'SECONDARY:'+','.join(sorted(x.strip().upper() for x in c.genealogy.secondary_changed_axes)),
        )
    return (
        c.causal_premise.strip().lower(), c.focal_interpretation.strip().lower(), c.knowledge_asymmetry.strip().lower(),
        c.option_change.strip().lower(), c.relationship_implication.strip().lower(), c.reader_effect.strip().lower(),
    )


def same_basin(a: CandidateConcept, b: CandidateConcept) -> bool:
    if a.genealogy is not None and b.genealogy is not None:
        return structural_signature(a)==structural_signature(b)
    sa,sb=structural_signature(a),structural_signature(b)
    different=sum(x!=y for x,y in zip(sa,sb))
    assumption_diff=set(a.changed_assumptions)!=set(b.changed_assumptions)
    return different<2 and not assumption_diff


def cross_examine_candidates(candidates:tuple[CandidateConcept,...]|list[CandidateConcept]) -> tuple[CrossExamRecord,...]:
    candidates=tuple(candidates); failure_map={c.candidate_id:[] for c in candidates}
    for c in candidates:
        if c.genealogy and c.genealogy.sibling_visibility:
            failure_map[c.candidate_id].append('CANDIDATE_INDEPENDENCE_VIOLATION')
        if c.search_mode is CreativeSearchMode.TRANSFORM and not c.changed_assumptions:
            failure_map[c.candidate_id].append('TRANSFORM_WITHOUT_CHANGED_ASSUMPTION')
    for i,a in enumerate(candidates):
        for b in candidates[i+1:]:
            if same_basin(a,b):
                failure_map[a.candidate_id].append('CANDIDATE_BASIN_COLLAPSE')
                failure_map[b.candidate_id].append('CANDIDATE_BASIN_COLLAPSE')
    return tuple(CrossExamRecord(c.candidate_id,tuple(dict.fromkeys(failure_map[c.candidate_id]))) for c in candidates)


def next_search_mode(previous_modes:tuple[CreativeSearchMode,...]|list[CreativeSearchMode], failure_signature:str) -> CreativeSearchMode:
    used=set(previous_modes)
    order=(CreativeSearchMode.EXPLORE,CreativeSearchMode.REFRAME,CreativeSearchMode.TRANSFORM,CreativeSearchMode.COMBINE)
    for mode in order:
        if mode not in used: return mode
    raise ValueError(f'STRUCTURAL_SEARCH_EXHAUSTED:{failure_signature}')


def build_search_receipt(decision:SearchDecision, candidates=()) -> SearchReceipt:
    candidates=tuple(candidates)
    if decision.path is SearchPath.DIRECT:
        return SearchReceipt(decision,status='NOT_REQUIRED')
    if not candidates:
        return SearchReceipt(decision,status='SEARCH_REQUIRED')
    cross=cross_examine_candidates(candidates)
    admissible=[c for c,r in zip(candidates,cross) if not r.failures]
    selected=admissible[0] if admissible else None
    return SearchReceipt(decision,candidates,cross,selected,(), 'COMPLETE' if selected else 'ASSURANCE_NOT_MET')


def winner_dominant_synthesis(
    winner: CandidateConcept,
    alternatives: list[CandidateConcept] | tuple[CandidateConcept, ...],
    *, bounded_contributions: dict[str, list[str]] | None = None,
) -> SynthesizedConcept:
    bounded_contributions = bounded_contributions or {}
    contributions: list[str] = []
    alt_ids = {a.candidate_id for a in alternatives}
    for cid, values in bounded_contributions.items():
        if cid not in alt_ids: continue
        contributions.extend(str(v) for v in values if str(v).strip())
    return SynthesizedConcept(
        winner_id=winner.candidate_id, causal_premise=winner.causal_premise,
        focal_interpretation=winner.focal_interpretation, knowledge_asymmetry=winner.knowledge_asymmetry,
        option_change=winner.option_change, relationship_implication=winner.relationship_implication,
        reader_effect=winner.reader_effect, contributions=tuple(contributions[:6]),
    )


def conception_to_packet(concept: CandidateConcept | None) -> dict:
    if concept is None: return {}
    return {
        'conception_id':concept.candidate_id,'dominant_causal_premise':concept.causal_premise,
        'focal_interpretation':concept.focal_interpretation,'knowledge_asymmetry':concept.knowledge_asymmetry,
        'option_change':concept.option_change,'relationship_implication':concept.relationship_implication,
    }
