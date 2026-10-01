from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from copy import deepcopy


def freeze(value):
    if isinstance(value, MappingProxyType):
        return value
    if isinstance(value, dict):
        return MappingProxyType({k: freeze(v) for k, v in deepcopy(value).items()})
    if isinstance(value, (set, frozenset)):
        return frozenset(freeze(v) for v in value)
    if isinstance(value, list):
        return tuple(freeze(v) for v in value)
    if isinstance(value, tuple):
        return tuple(freeze(v) for v in value)
    return deepcopy(value)


class EvidenceReliability(str, Enum):
    VERIFIED = 'VERIFIED'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    UNKNOWN = 'UNKNOWN'
    DECEPTIVE = 'DECEPTIVE'


@dataclass(frozen=True)
class DiegeticEvidence:
    evidence_id: str
    kind: str
    claim: object
    source_actor: str | None
    reliability: EvidenceReliability = EvidenceReliability.UNKNOWN
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ActorCognition:
    actor_id: str
    stored_knowledge: frozenset[str] = field(default_factory=frozenset)
    active_knowledge: frozenset[str] = field(default_factory=frozenset)
    remembered_model: object = field(default_factory=dict)
    beliefs: object = field(default_factory=dict)
    self_model: object = field(default_factory=dict)
    disclosure: object = field(default_factory=dict)
    active_goals: tuple[str, ...] = ()
    suppressed_goals: tuple[str, ...] = ()
    perceived_affordances: tuple[str, ...] = ()
    affective_residue: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, 'stored_knowledge', frozenset(self.stored_knowledge))
        object.__setattr__(self, 'active_knowledge', frozenset(self.active_knowledge))
        object.__setattr__(self, 'remembered_model', freeze(self.remembered_model))
        object.__setattr__(self, 'beliefs', freeze(self.beliefs))
        object.__setattr__(self, 'self_model', freeze(self.self_model))
        object.__setattr__(self, 'disclosure', freeze(self.disclosure))
        object.__setattr__(self, 'active_goals', tuple(self.active_goals))
        object.__setattr__(self, 'suppressed_goals', tuple(self.suppressed_goals))
        object.__setattr__(self, 'perceived_affordances', tuple(self.perceived_affordances))
        object.__setattr__(self, 'affective_residue', tuple(self.affective_residue))

@dataclass(frozen=True)
class AffordanceField:
    objective: frozenset[str] = field(default_factory=frozenset)
    perceived_by_actor: object = field(default_factory=dict)
    relational_permissions: object = field(default_factory=dict)
    institutional_permissions: object = field(default_factory=dict)
    costs: object = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, 'objective', frozenset(self.objective))
        object.__setattr__(self, 'perceived_by_actor', freeze(self.perceived_by_actor))
        object.__setattr__(self, 'relational_permissions', freeze(self.relational_permissions))
        object.__setattr__(self, 'institutional_permissions', freeze(self.institutional_permissions))
        object.__setattr__(self, 'costs', freeze(self.costs))


@dataclass(frozen=True)
class InteractionFrame:
    frame_id: str
    label: str
    evidence_refs: tuple[str, ...] = ()
    permitted_moves: tuple[str, ...] = ()
    prohibited_moves: tuple[str, ...] = ()
    provisional: bool = True

    def __post_init__(self):
        object.__setattr__(self, 'evidence_refs', tuple(self.evidence_refs))
        object.__setattr__(self, 'permitted_moves', tuple(self.permitted_moves))
        object.__setattr__(self, 'prohibited_moves', tuple(self.prohibited_moves))

@dataclass(frozen=True)
class MemoryRecord:
    memory_id: str
    remembered_value: object
    distorted: bool = False
    evidence_refs: tuple[str, ...] = ()
    def __post_init__(self):
        object.__setattr__(self,'evidence_refs',tuple(self.evidence_refs))
        if self.distorted and not self.evidence_refs:
            raise ValueError('UNGROUNDED_MEMORY_DISTORTION')


@dataclass(frozen=True)
class SelfModelGap:
    believed_motive: str
    behavior_policy_evidence: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    def __post_init__(self):
        object.__setattr__(self,'behavior_policy_evidence',tuple(self.behavior_policy_evidence))
        object.__setattr__(self,'evidence_refs',tuple(self.evidence_refs))


@dataclass(frozen=True)
class ActiveCognitiveSet:
    actor_id: str
    active_knowledge: tuple[str, ...] = ()
    active_beliefs: object = field(default_factory=dict)
    active_uncertainties: tuple[str, ...] = ()
    active_memories: object = field(default_factory=dict)
    active_goals: tuple[str, ...] = ()
    active_relationship_tensions: tuple[str, ...] = ()
    immediate_body_state: object = field(default_factory=dict)
    current_attention_targets: tuple[str, ...] = ()
    def __post_init__(self):
        object.__setattr__(self,'active_knowledge',tuple(self.active_knowledge))
        object.__setattr__(self,'active_beliefs',freeze(self.active_beliefs))
        object.__setattr__(self,'active_uncertainties',tuple(self.active_uncertainties))
        object.__setattr__(self,'active_memories',freeze(self.active_memories))
        object.__setattr__(self,'active_goals',tuple(self.active_goals))
        object.__setattr__(self,'active_relationship_tensions',tuple(self.active_relationship_tensions))
        object.__setattr__(self,'immediate_body_state',freeze(self.immediate_body_state))
        object.__setattr__(self,'current_attention_targets',tuple(self.current_attention_targets))


def build_active_cognitive_set(actor_id: str, state: dict) -> ActiveCognitiveSet:
    narrative=state.get('narrative_state',{}) if isinstance(state.get('narrative_state'),dict) else {}
    active_map=narrative.get('active_knowledge_by_actor',{}) if isinstance(narrative.get('active_knowledge_by_actor'),dict) else {}
    beliefs_map=narrative.get('beliefs_by_actor',{}) if isinstance(narrative.get('beliefs_by_actor'),dict) else {}
    memory_map=narrative.get('remembered_models_by_actor',{}) if isinstance(narrative.get('remembered_models_by_actor'),dict) else {}
    actor_states=state.get('actor_states',{}) if isinstance(state.get('actor_states'),dict) else {}
    actor=actor_states.get(actor_id,{}) if isinstance(actor_states.get(actor_id,{}),dict) else {}
    rel=state.get('relationship_state',{}) if isinstance(state.get('relationship_state'),dict) else {}
    tensions=rel.get('active_tensions',()) if isinstance(rel,dict) else ()
    voice=state.get('voice_state',{}) if isinstance(state.get('voice_state'),dict) else {}
    return ActiveCognitiveSet(
        actor_id=actor_id,
        active_knowledge=tuple(active_map.get(actor_id,())),
        active_beliefs=beliefs_map.get(actor_id,{}),
        active_uncertainties=tuple(narrative.get('relevant_unknowns',state.get('relevant_unknowns',())) or ()),
        active_memories=memory_map.get(actor_id,{}),
        active_goals=tuple(actor.get('active_goals',())),
        active_relationship_tensions=tuple(tensions or ()),
        immediate_body_state=actor.get('body_state',{}),
        current_attention_targets=tuple(voice.get('attention_habits',actor.get('attention_bias',())) or ()),
    )


@dataclass(frozen=True)
class EpistemicActionEligibility:
    eligible: bool
    reasons: tuple[str, ...] = ()


def evaluate_epistemic_action(uncertainty_material: bool, information_value: bool, locally_rational: bool) -> EpistemicActionEligibility:
    reasons=[]
    if not uncertainty_material: reasons.append('NO_MATERIAL_UNCERTAINTY')
    if not information_value: reasons.append('NO_INFORMATION_VALUE')
    if not locally_rational: reasons.append('NOT_LOCALLY_RATIONAL')
    return EpistemicActionEligibility(not reasons,tuple(reasons))


@dataclass(frozen=True)
class StrategicAgentState:
    agent_id: str
    objective: str
    reachable_knowledge: tuple[str, ...] = ()
    beliefs: object = field(default_factory=dict)
    current_strategy: tuple[str, ...] = ()
    risk_tolerance: str = 'UNKNOWN'
    resources: tuple[str, ...] = ()
    def __post_init__(self):
        object.__setattr__(self,'reachable_knowledge',tuple(self.reachable_knowledge))
        object.__setattr__(self,'beliefs',freeze(self.beliefs))
        object.__setattr__(self,'current_strategy',tuple(self.current_strategy))
        object.__setattr__(self,'resources',tuple(self.resources))


@dataclass(frozen=True)
class StrategicAgentView:
    agent_id: str
    objective: str
    reachable_knowledge: tuple[str, ...]
    beliefs: object
    current_strategy: tuple[str, ...]
    risk_tolerance: str
    resources: tuple[str, ...]


def project_strategic_agent(state: StrategicAgentState, *, objective_world_truth=()) -> StrategicAgentView:
    # objective_world_truth is deliberately not merged: planner truth does not grant agent knowledge.
    return StrategicAgentView(state.agent_id,state.objective,tuple(state.reachable_knowledge),state.beliefs,
                              tuple(state.current_strategy),state.risk_tolerance,tuple(state.resources))
