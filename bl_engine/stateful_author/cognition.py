from __future__ import annotations
from dataclasses import dataclass


def route_cognition(scene: dict) -> set[str]:
    routes:set[str]=set()
    if scene.get('mystery'): routes.add('belief_evidence_map')
    if scene.get('flashback'): routes.add('memory_relevance')
    if scene.get('reveal'): routes.add('reveal_accounting')
    if scene.get('relationship_pivot'): routes.add('relationship_evidence')
    if scene.get('deception'): routes.add('claim_knowledge_map')
    if scene.get('epistemic_action'): routes.add('epistemic_action')
    if scene.get('strategic_ecology'): routes.add('strategic_ecology')
    if scene.get('candidate_search'): routes.add('candidate_genealogy')
    return routes


@dataclass(frozen=True)
class RevealArtifact:
    prior_model:str=''
    plausible_evidence:tuple[str,...]=()
    preserved_truth:tuple[str,...]=()
    recoded_element:tuple[str,...]=()
    forward_consequence:tuple[str,...]=()
    reveal_mode:str='LOCAL'

@dataclass(frozen=True)
class RelationshipArtifact:
    prior_evidence:tuple[str,...]=()
    changed_dimensions:tuple[str,...]=()
    cost:tuple[str,...]=()
    observable_behavior:tuple[str,...]=()
    permission_change:tuple[str,...]=()

@dataclass(frozen=True)
class MysteryArtifact:
    visible_evidence:tuple[str,...]=()
    focal_model:tuple[str,...]=()
    reader_models:tuple[str,...]=()
    withheld_or_unknown_class:str='UNKNOWN'
    retrieval_support:tuple[str,...]=()

@dataclass(frozen=True)
class CharacterDecisionArtifact:
    reachable_evidence:tuple[str,...]=()
    active_goals:tuple[str,...]=()
    bias:tuple[str,...]=()
    perceived_options:tuple[str,...]=()
    rejected_author_optimal_option:str=''

@dataclass(frozen=True)
class RecurrenceArtifact:
    prior_meaning:str=''
    changed_condition:tuple[str,...]=()
    new_function:str=''


def build_cognition_artifact(kind:str, data:dict):
    if kind=='reveal_accounting': return RevealArtifact(**{k:v for k,v in data.items() if k in RevealArtifact.__dataclass_fields__})
    if kind=='relationship_evidence': return RelationshipArtifact(**{k:v for k,v in data.items() if k in RelationshipArtifact.__dataclass_fields__})
    if kind=='belief_evidence_map': return MysteryArtifact(**{k:v for k,v in data.items() if k in MysteryArtifact.__dataclass_fields__})
    if kind=='character_decision': return CharacterDecisionArtifact(**{k:v for k,v in data.items() if k in CharacterDecisionArtifact.__dataclass_fields__})
    if kind=='recurrence_recode': return RecurrenceArtifact(**{k:v for k,v in data.items() if k in RecurrenceArtifact.__dataclass_fields__})
    raise ValueError(f'UNKNOWN_COGNITION_ARTIFACT:{kind}')
