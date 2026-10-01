from pathlib import Path
import pytest

from stateful_author.intelligence import load_intelligence_library, SceneSignal, SignalSource
from stateful_author.runtime import SceneContract, prepare_scene, state_hash
from stateful_author.creative import (
    SearchPath, CreativeSearchMode, AxiomClass, GenerativeAxiom, CandidateGenealogy,
    CandidateConcept, distinguish_scene, decide_search, same_basin, authorize_transform,
    cross_examine_candidates, next_search_mode, winner_dominant_synthesis,
)

ROOT=Path(__file__).resolve().parents[1]
LIB=load_intelligence_library(ROOT/'author/intelligence/cards')
STATE={'_version':'v1','narrative_state':{'knowledge_by_actor':{'A':[]}}}


def grounded(name,value=True):
    return SceneSignal(name,value,.95,(f'e:{name}',),SignalSource.TEXT_OBSERVED,'HIGH')


def test_search_controller_routes_ordinary_scene_direct_and_major_reveal_high_assurance():
    c=SceneContract('s','A','write',parent_state_version='v1')
    ordinary=distinguish_scene(c,{},STATE)
    assert decide_search(c,ordinary).path is SearchPath.DIRECT
    reveal=distinguish_scene(c,{'major_reveal':grounded('major_reveal')},STATE)
    assert decide_search(c,reveal).path is SearchPath.HIGH_ASSURANCE


def test_open_creative_request_can_raise_search_without_faking_high_risk_signal():
    c=SceneContract('s','A','find an unusual conception',creative_freedom='OPEN',parent_state_version='v1')
    decision=decide_search(c,distinguish_scene(c,{},STATE))
    assert decision.path in {SearchPath.LIGHT_EXPLORE,SearchPath.HIGH_ASSURANCE}
    assert decision.reason


def test_hard_anchor_cannot_be_transformed_but_model_default_can():
    hard=GenerativeAxiom('a1','door must stay locked',AxiomClass.HARD_ANCHOR,('canon:door',),False)
    with pytest.raises(ValueError,match='AXIOM_TRANSFORM_FORBIDDEN'):
        authorize_transform(hard)
    model=GenerativeAxiom('a2','conflict ends in confession',AxiomClass.MODEL_DEFAULT,(),True)
    assert authorize_transform(model).axiom_id=='a2'


def test_same_basin_uses_structural_genealogy_not_surface_paraphrase():
    g1=CandidateGenealogy(('goal-default',),('canon-lock',),'GOAL',(), 'MODEL_DEFAULT',(),())
    a=CandidateConcept('A',CreativeSearchMode.EXPLORE,('goal-default',),'He stays to get an answer','He reads silence as refusal','A knows less','Leaving seems costly','No permission change','Reader expects conflict',genealogy=g1)
    b=CandidateConcept('B',CreativeSearchMode.EXPLORE,('goal-default',),'He remains because he wants a reply','Silence looks like rejection','Knowledge still favors B','Exit has a cost','Relationship boundary unchanged','Conflict remains expected',genealogy=g1)
    assert same_basin(a,b)
    g2=CandidateGenealogy(('knowledge-default',),('canon-lock',),'KNOWLEDGE',(), 'EVIDENCE',(),())
    c=CandidateConcept('C',CreativeSearchMode.REFRAME,('knowledge-default',),'He tests what B knows','He treats silence as evidence','A plants false info','Questioning becomes useful','Testing boundary','Reader updates culprit model',genealogy=g2)
    assert not same_basin(a,c)


def test_cross_exam_flags_candidate_sibling_visibility_and_basin_collapse():
    badg=CandidateGenealogy(('x',),(),'GOAL',(), 'MODEL_DEFAULT',(),('B',))
    a=CandidateConcept('A',CreativeSearchMode.EXPLORE,('x',),'c','f','k','o','r','reader',genealogy=badg)
    b=CandidateConcept('B',CreativeSearchMode.EXPLORE,('x',),'c2','f2','k2','o2','r2','reader2',genealogy=CandidateGenealogy(('x',),(),'GOAL',(), 'MODEL_DEFAULT',(),()))
    records=cross_examine_candidates((a,b))
    assert any('CANDIDATE_INDEPENDENCE_VIOLATION' in r.failures for r in records)
    assert any('CANDIDATE_BASIN_COLLAPSE' in r.failures for r in records)


def test_repeated_basin_failure_changes_strategy_instead_of_surface_retry():
    first=next_search_mode((), 'CANDIDATE_BASIN_COLLAPSE')
    second=next_search_mode((first,), 'CANDIDATE_BASIN_COLLAPSE')
    assert first != second


def test_prepare_scene_integrates_search_decision_and_conception_without_candidate_prose():
    c=SceneContract('s','A','write',parent_state_version='v1',parent_state_hash=state_hash(STATE))
    prepared=prepare_scene(c,STATE,LIB,scene_signals={'major_reveal':grounded('major_reveal')})
    assert prepared.search_receipt.decision.path is SearchPath.HIGH_ASSURANCE
    assert prepared.search_receipt.candidate_texts == ()
    assert 'scene_distinction' not in prepared.writer_packet


def test_winner_synthesis_does_not_average_causal_premise():
    a=CandidateConcept('A',CreativeSearchMode.EXPLORE,('x',),'causal A','f','k','o','r','reader')
    b=CandidateConcept('B',CreativeSearchMode.REFRAME,('y',),'causal B','f2','k2','o2','r2','reader2')
    out=winner_dominant_synthesis(a,[b],bounded_contributions={'B':['constraint only']})
    assert out.causal_premise=='causal A'
    assert out.contributions==('constraint only',)
