from pathlib import Path
from dataclasses import replace
import jsonschema, json

from stateful_author.intelligence import load_intelligence_library, AuthorizedIntelligencePayload
from stateful_author.runtime import SceneContract, prepare_scene
from stateful_author.packet import build_writer_packet
from stateful_author.projection import ActorView, RealizationPacket, project_actor_view

ROOT=Path(__file__).resolve().parents[1]
LIB=load_intelligence_library(ROOT/'author/intelligence/cards')


def _state():
    return {
        '_version':'v1',
        'narrative_state': {
            'knowledge_by_actor': {'A':['door_locked'], 'B':['master_secret']},
            'active_knowledge_by_actor': {'A':['door_locked']},
            'beliefs_by_actor': {'A': {'visitor':'late'}},
            'remembered_models_by_actor': {'A': {'last_night':'blurred'}},
            'self_models_by_actor': {'A': {'motive':'money'}},
            'relevant_unknowns': ['culprit'],
            'hidden_master_plan': 'THE FOCAL CHARACTER MUST NOT KNOW THIS',
            'objective_affordances': ['front_door','secret_exit'],
            'perceived_affordances_by_actor': {'A':['front_door']},
        },
        'relationship_state': {'distance':'guarded','permissions':['share_table']},
        'reader_model': {'correct_answer':'B','hidden_reader_target':'choose A'},
        'affordances': {'objective':['secret_exit'], 'perceived_by_actor':{'A':['front_door']}},
        'event': {'visible_action':'rain hits window'},
        'voice_state': {'attention_habits':['cost'], 'judgment_logic':['usable_or_not']},
    }


def test_actor_view_contains_only_focal_reachable_and_perceived_state():
    view=project_actor_view('A', _state())
    assert view.focal_id == 'A'
    assert 'door_locked' in view.active_knowledge
    assert 'master_secret' not in view.reachable_facts
    assert 'front_door' in view.perceived_options
    assert 'secret_exit' not in view.perceived_options


def test_realization_packet_preserves_focal_and_narrator_mode_exactly():
    c=SceneContract('s','A','write',parent_state_version='v1',narrator_mode='FIRST_PERSON_LIMITED')
    p=build_writer_packet(c,_state(),[],LIB)
    assert p['scene']['focal_id']=='A'
    assert p['scene']['narrator_mode']=='FIRST_PERSON_LIMITED'


def test_official_writer_packet_cannot_leak_raw_or_omniscient_state():
    c=SceneContract('s','A','write',parent_state_version='v1')
    p=build_writer_packet(c,_state(),[],LIB)
    blob=json.dumps(p,ensure_ascii=False)
    for forbidden in ['hidden_master_plan','THE FOCAL CHARACTER MUST NOT KNOW THIS','correct_answer','hidden_reader_target','secret_exit','reader_model','narrative_state','affordances']:
        assert forbidden not in blob


def test_writer_packet_transports_concrete_specialist_artifact_not_generic_guidance():
    c=SceneContract('s','A','write',parent_state_version='v1')
    payload=AuthorizedIntelligencePayload('RELATIONSHIP_EVIDENCE', LIB['RELATIONSHIP_EVIDENCE'].version,
        ('generic theory line should not reach writer',),
        (('relationship_state','distance=guarded'),('permission','share_table')))
    p=build_writer_packet(c,_state(),[payload],LIB)
    assert p['cognition_artifacts'][0]['specialist_id']=='RELATIONSHIP_EVIDENCE'
    assert p['cognition_artifacts'][0]['artifact']['relationship_state']=='distance=guarded'
    assert 'generic theory line should not reach writer' not in json.dumps(p)


def test_writer_packet_schema_is_positive_allow_list():
    c=SceneContract('s','A','write',parent_state_version='v1')
    p=build_writer_packet(c,_state(),[],LIB)
    schema=json.loads((ROOT/'runtime/WRITER_PACKET_SCHEMA.json').read_text())
    jsonschema.validate(p,schema)
    bad=dict(p); bad['raw_narrative_state']={}
    try:
        jsonschema.validate(bad,schema)
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError('positive allow-list accepted raw_narrative_state')


def test_prepare_scene_official_packet_uses_projection_compiler():
    from stateful_author.runtime import state_hash
    state=_state()
    c=SceneContract('s','A','write',parent_state_version='v1',narrator_mode='FOCAL_CLOSE',parent_state_hash=state_hash(state))
    prepared=prepare_scene(c,state,LIB,scene_signals={})
    assert prepared.writer_packet['scene']['narrator_mode']=='FOCAL_CLOSE'
    assert 'reader_model' not in prepared.writer_packet


def test_writer_packet_does_not_promote_inactive_stored_knowledge_into_reachable_now():
    s=_state()
    s['narrative_state']['knowledge_by_actor']['A']=['door_locked','old_secret_that_is_not_active']
    s['narrative_state']['active_knowledge_by_actor']['A']=['door_locked']
    from stateful_author.runtime import state_hash
    c=SceneContract('s','A','write',parent_state_version='v1',parent_state_hash=state_hash(s))
    p=build_writer_packet(c,s,[],LIB)
    blob=json.dumps(p,ensure_ascii=False)
    assert 'door_locked' in blob
    assert 'old_secret_that_is_not_active' not in blob


def test_verifier_can_detect_exact_unreachable_fact_even_without_caller_supplied_unreachable_count():
    s=_state()
    from stateful_author.runtime import state_hash, verify_proposal
    c=SceneContract('leak','A','write',parent_state_version='v1',parent_state_hash=state_hash(s))
    prepared=prepare_scene(c,s,LIB,scene_signals={})
    assert 'master_secret' not in json.dumps(prepared.writer_packet,ensure_ascii=False)
    record=verify_proposal(prepared,text='master_secret',context={})
    assert record.qualification.value=='FAIL'
    assert any(x.startswith('KNOWLEDGE_LEAK:') for x in record.failures)
