from pathlib import Path
import pytest

from stateful_author.epistemic import (
    ActorCognition, MemoryRecord, build_active_cognitive_set, SelfModelGap,
    evaluate_epistemic_action, StrategicAgentState, project_strategic_agent,
)
from stateful_author.reader import (
    HypothesisStatus, ReaderHypothesis, ReaderModel, build_reader_view,
    reactivate_evidence, evidence_gain_without_answer_gain,
)
from stateful_author.interaction import UptakeEvidence, confirm_interaction_frame
from stateful_author.serial import EpisodeDelta, PressureVector
from stateful_author.commercial import evaluate_commercial_arc
from stateful_author.runtime import SceneContract, prepare_scene, state_hash
from stateful_author.intelligence import load_intelligence_library

ROOT=Path(__file__).resolve().parents[1]
LIB=load_intelligence_library(ROOT/'author/intelligence/cards')


def test_active_cognitive_set_does_not_promote_all_stored_knowledge():
    state={'narrative_state':{
        'knowledge_by_actor':{'A':['old_secret','door_locked']},
        'active_knowledge_by_actor':{'A':['door_locked']},
        'beliefs_by_actor':{'A':{'visitor':'late'}},
    }}
    active=build_active_cognitive_set('A',state)
    assert active.active_knowledge==('door_locked',)
    assert 'old_secret' not in active.active_knowledge


def test_memory_distortion_requires_grounded_reason_instead_of_fake_humanization():
    with pytest.raises(ValueError,match='UNGROUNDED_MEMORY_DISTORTION'):
        MemoryRecord('m1','wrong order',distorted=True,evidence_refs=())
    m=MemoryRecord('m1','wrong order',distorted=True,evidence_refs=('stress:e1',))
    assert m.distorted


def test_self_model_gap_preserves_believed_motive_and_behavior_evidence_without_resolving_truth():
    gap=SelfModelGap('money',('removed danger first','waited outside'),('scene:1','scene:2'))
    assert gap.believed_motive=='money'
    assert gap.behavior_policy_evidence[0]=='removed danger first'
    assert not hasattr(gap,'true_motive')


def test_epistemic_action_requires_uncertainty_value_and_local_rationality():
    assert evaluate_epistemic_action(True,True,True).eligible
    assert not evaluate_epistemic_action(False,True,True).eligible
    assert not evaluate_epistemic_action(True,False,True).eligible


def test_strategic_agent_projection_keeps_agent_partial_not_omniscient():
    s=StrategicAgentState('ORG','catch A',('camera_feed',),{'A':'injured'},('patrol',),'MEDIUM')
    view=project_strategic_agent(s, objective_world_truth=('secret_exit',))
    assert 'camera_feed' in view.reachable_knowledge
    assert 'secret_exit' not in view.reachable_knowledge


def test_reader_view_keeps_stale_evidence_separate_until_reactivated():
    h=ReaderHypothesis('h1','B lied',('clue:old',),'MEDIUM',True,status=HypothesisStatus.PLAUSIBLE)
    model=ReaderModel((h,),('Who lied?',),retrievable_evidence=('clue:new',),suppressed_evidence=('clue:old',),tractability='MEDIUM')
    view=build_reader_view(model)
    assert 'clue:old' in view.stale_evidence
    assert 'clue:old' not in view.active_evidence
    view2=reactivate_evidence(view,'clue:old','cue:present')
    assert 'clue:old' in view2.active_evidence


def test_evidence_gain_without_answer_gain_can_reweight_hypotheses_without_resolution():
    before={'A':HypothesisStatus.DOMINANT,'B':HypothesisStatus.PLAUSIBLE}
    after={'A':HypothesisStatus.PLAUSIBLE,'B':HypothesisStatus.DOMINANT}
    result=evidence_gain_without_answer_gain(before,after,answer_revealed=False)
    assert result.progress and not result.answer_gain


def test_emergent_interaction_frame_requires_generated_action_and_grounded_uptake():
    ungrounded=UptakeEvidence('A offers umbrella','B reads pity','BARGAIN',())
    assert not confirm_interaction_frame('CARE',ungrounded).confirmed
    grounded=UptakeEvidence('A offers umbrella','B refuses and names debt','BARGAIN',('span:a','span:b'))
    out=confirm_interaction_frame('CARE',grounded)
    assert out.confirmed and out.new_frame=='BARGAIN'


def test_nontransformative_scene_metabolism_is_not_false_progress_failure():
    episodes=[
        {'delta':EpisodeDelta(metabolism='INHABIT'),'pressure':PressureVector()},
        {'delta':EpisodeDelta(metabolism='RECOVER'),'pressure':PressureVector()},
        {'delta':EpisodeDelta(metabolism='INCUBATE'),'pressure':PressureVector()},
    ]
    result=evaluate_commercial_arc(episodes,[])
    assert 'FALSE_PROGRESS' not in result.failures
    assert result.vector['episode_delta_coverage']==0.0


def test_prepare_scene_keeps_reader_model_planner_side_and_attaches_active_cognitive_set():
    state={'_version':'v1','narrative_state':{
        'knowledge_by_actor':{'A':['x','y']},'active_knowledge_by_actor':{'A':['y']},
    },'reader_model':ReaderModel(active_questions=('What?',))}
    c=SceneContract('s','A','write',parent_state_version='v1',parent_state_hash=state_hash(state))
    prepared=prepare_scene(c,state,LIB,scene_signals={})
    assert prepared.active_cognitive_set.active_knowledge==('y',)
    assert prepared.reader_view.active_questions==('What?',)
    assert 'reader_model' not in prepared.writer_packet
