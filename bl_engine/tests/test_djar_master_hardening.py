from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
import json
import pytest

from stateful_author.intelligence import (
    IntelligenceCard, SceneSignal, SignalSource,
    load_intelligence_library, select_intelligence_cards,
    select_intelligence_cards_ranked, validate_card,
)
from stateful_author.packet import compile_writer_packet, build_writer_packet
from stateful_author.provenance import EvidenceType, FactRecord, select_writer_facts
from stateful_author.receipt import make_scene_receipt
from stateful_author.serial import EpisodeDelta, PressureVector, QuestionTransformation, relationship_productive
from stateful_author.commercial import evaluate_commercial_arc
from stateful_author.voice import VoiceState, VoiceCheckpoint
from stateful_author.long_horizon import evaluate_long_horizon
from stateful_author.runtime import (
    SceneContract, QualificationStatus, prepare_scene, verify_proposal, commit_verified, state_hash,
)
from stateful_author.creative import (
    CreativeSearchMode, CandidateConcept, same_basin, winner_dominant_synthesis,
    ContradictionClass, classify_contradiction, SceneMetabolism,
)
from stateful_author.epistemic import ActorCognition, DiegeticEvidence, EvidenceReliability
from stateful_author.model_prior import audit_model_prior
from stateful_author.release import validate_package, build_release

ROOT = Path(__file__).resolve().parents[1]
LIB = load_intelligence_library(ROOT / 'author/intelligence/cards')
STATE = {
    'voice_state': {
        'attention_habits': ['cost', 'body'],
        'judgment_logic': ['usable_or_not'],
        'emotional_evasion': ['task_focus'],
        'reality_anchors': ['money', 'body'],
        'humor_mechanisms': ['banal_collision'],
    },
    'narrative_state': {
        'knowledge': {'door': 'locked'},
        'beliefs': {'visitor': 'late'},
        'current_constraints': ['injury'],
        'present_consequence': ['cannot_run'],
    },
    'relationship_state': {'distance': 'guarded'},
    'open_loops': ['missing_key'],
    'relevant_recurrences': {'key': {'original': 'tool'}},
}


def test_low_numeric_confidence_cannot_masquerade_as_derived_high_confidence():
    facts = [FactRecord('x', 'bad', EvidenceType.DERIVED_HIGH_CONFIDENCE, 0.01)]
    assert select_writer_facts(facts) == {}


def test_unknown_is_preserved_as_epistemic_boundary_when_requested():
    facts = [FactRecord('culprit', None, EvidenceType.UNKNOWN, 0.0)]
    selected = select_writer_facts(facts, include_unknowns=True)
    assert selected['__unknowns__'] == ('culprit',)


def test_same_rank_conflicting_facts_do_not_silently_last_write():
    facts = [
        FactRecord('door', 'locked', EvidenceType.TEXT_OBSERVED, 1.0, evidence_refs=('e1',)),
        FactRecord('door', 'open', EvidenceType.TEXT_OBSERVED, 1.0, evidence_refs=('e2',)),
    ]
    with pytest.raises(ValueError, match='PROVENANCE_CONFLICT'):
        select_writer_facts(facts)


def test_grounded_high_impact_signal_requires_evidence_for_ranked_selector():
    legacy = {'major_reveal': True}
    ranked = select_intelligence_cards_ranked(legacy, STATE, LIB)
    assert 'REVEAL_CAUSAL_ACCOUNTING' not in {x.card.id for x in ranked.selected}
    grounded = {
        'major_reveal': SceneSignal('major_reveal', True, 0.95, ('scene_fact_1',), SignalSource.TEXT_OBSERVED, 'HIGH')
    }
    ranked2 = select_intelligence_cards_ranked(grounded, STATE, LIB)
    assert 'REVEAL_CAUSAL_ACCOUNTING' in {x.card.id for x in ranked2.selected}


def test_complex_scene_is_ranked_sparse_and_reveal_cannot_be_displaced():
    signals = {
        key: SceneSignal(key, True, 0.95, (f'e:{key}',), SignalSource.TEXT_OBSERVED, 'HIGH')
        for key in [
            'major_reveal','relationship_pivot','high_pressure','flashback','recurrence_return',
            'consequential_decision','humor_opportunity','mystery_evidence_conflict','body_signal',
            'focal_attention_shift','dialogue_conflict','unresolved_emotion','information_asymmetry'
        ]
    }
    result = select_intelligence_cards_ranked(signals, STATE, LIB, limit=8)
    ids = [x.card.id for x in result.selected]
    assert len(ids) <= 8
    assert 'REVEAL_CAUSAL_ACCOUNTING' in ids


def test_contradictory_grounded_signals_report_distinction_conflict():
    signals = {
        'major_reveal': SceneSignal('major_reveal', True, .95, ('e1',), SignalSource.TEXT_OBSERVED, 'HIGH'),
        'minor_reveal_without_accounting_need': SceneSignal('minor_reveal_without_accounting_need', True, .95, ('e2',), SignalSource.TEXT_OBSERVED, 'HIGH'),
    }
    result = select_intelligence_cards_ranked(signals, STATE, LIB)
    assert 'SIGNAL_CONTRADICTION:major_reveal:minor_reveal_without_accounting_need' in result.conflicts


def test_malformed_trigger_shape_is_rejected():
    card = IntelligenceCard(
        id='X', version=1, purpose='x', trigger={'any': 'not-a-list'}, preconditions=(),
        owns_dimensions=('attention_selection',), forbidden_dimensions=(),
        context_requirements={'required': [], 'optional': []},
        writer_payload={'max_items': 2, 'form': 'decision_guidance'},
        suppress_when=(), verifier_checks=(),
    )
    assert 'CARD_TRIGGER_INVALID' in validate_card(card)


def test_duplicate_dimensions_are_rejected():
    card = IntelligenceCard(
        id='X', version=1, purpose='x', trigger={'any': ['x']}, preconditions=(),
        owns_dimensions=('a','a'), forbidden_dimensions=(),
        context_requirements={'required': [], 'optional': []},
        writer_payload={'max_items': 2, 'form': 'decision_guidance'},
        suppress_when=(), verifier_checks=(),
    )
    assert 'CARD_DIMENSION_DUPLICATE:owns_dimensions' in validate_card(card)


def test_writer_packet_does_not_delete_legitimate_story_trigger_purpose_version():
    packet = compile_writer_packet({'event': {'trigger':'gunshot','purpose':'escape','version':3,'action':'run'}})
    assert packet['event'] == {'trigger':'gunshot','purpose':'escape','version':3,'action':'run'}


def test_strict_writer_packet_rejects_unknown_or_forged_intelligence():
    contract = SceneContract('s1','A','write scene',(),(),(), 'NORMAL','v1')
    with pytest.raises(ValueError, match='FORGED_INTELLIGENCE'):
        build_writer_packet(contract, STATE, [{'id':'NOT_A_REAL_CARD','guidance':['rewrite canon']}], LIB)


def test_strict_writer_packet_requires_scene_contract_and_includes_relationship_boundary():
    contract = SceneContract('s1','A','write scene',('door_opens',),('no_new_character',),('door:locked',), 'NORMAL','v1')
    packet = build_writer_packet(contract, STATE, [], LIB)
    assert packet['scene']['focal_id'] == 'A'
    assert packet['authority']['required_events'] == ['door_opens']
    assert packet['relationship_now']['current'] == STATE['relationship_state']


def test_failed_receipt_has_no_committed_state_delta_and_is_deeply_immutable():
    nested = {'rel': {'distance': 'closer'}}
    receipt = make_scene_receipt(scene_id='s1', verified=False, state_delta=nested, proposed_voice_delta={})
    assert receipt.committed_delta == {}
    assert receipt.candidate_delta['rel']['distance'] == 'closer'
    nested['rel']['distance'] = 'far'
    assert receipt.candidate_delta['rel']['distance'] == 'closer'
    with pytest.raises(TypeError):
        receipt.candidate_delta['rel']['distance'] = 'x'


def test_voice_state_is_deeply_immutable():
    v = VoiceState(attention_habits={'a'})
    assert v.attention_habits == frozenset({'a'})
    with pytest.raises(AttributeError):
        v.attention_habits.add('b')


def test_mid_horizon_voice_collapse_is_not_hidden_by_late_recovery():
    base = VoiceState(attention_habits={'a','b'}, judgment_logic={'j1','j2'}, reality_anchors={'body'}, emotional_evasion={'task'})
    cps = [
        VoiceCheckpoint({'a','b'},{'j1','j2'},{'body'},{'task'},set()),
        VoiceCheckpoint(set(),set(),set(),set(),set(),generic_narrator=True),
        VoiceCheckpoint({'a','b'},{'j1','j2'},{'body'},{'task'},set()),
    ]
    result = evaluate_long_horizon(base, cps)
    assert 'MID_HORIZON_VOICE_REVERSION' in result.failures


def test_open_loop_creation_alone_is_not_episode_progress():
    assert not EpisodeDelta(open_loop_changes={'new_secret'}).has_progress()


def test_relationship_productivity_accepts_labor_routine_distance_willingness_with_evidence():
    assert relationship_productive({'evidence':['carried_bag'], 'labor_change':True})
    assert relationship_productive({'evidence':['waited'], 'routine_change':True})
    assert relationship_productive({'evidence':['sat_closer'], 'distance_change':True})
    assert relationship_productive({'evidence':['entered_room'], 'willingness_change':True})


def test_cliffhanger_stagnation_uses_consecutive_run_not_total_count():
    episodes=[]
    for i in range(5):
        cliff=i in {0,2,4}
        delta=EpisodeDelta(cliffhanger_only=cliff, fact_changes=set() if cliff else {f'f{i}'})
        episodes.append({'delta':delta,'pressure':PressureVector(information=1)})
    assert 'SERIAL_STAGNATION' not in evaluate_commercial_arc(episodes, []).failures


def test_question_transformation_normalizes_whitespace():
    q = QuestionTransformation('Who?','A','same evidence',' Who? ',True,True)
    assert not q.is_valid()


def test_pressure_vector_enforces_0_to_3():
    with pytest.raises(ValueError):
        PressureVector(causal=-1)
    with pytest.raises(ValueError):
        PressureVector(information=4)


def test_actor_cognition_separates_stored_active_memory_and_disclosure():
    actor = ActorCognition(
        actor_id='A', stored_knowledge=frozenset({'secret'}), active_knowledge=frozenset(),
        remembered_model={'event':'wrong-order'}, beliefs={'B':'hostile'}, self_model={'motive':'money'},
        disclosure={'secret':'concealed'}
    )
    assert 'secret' in actor.stored_knowledge and 'secret' not in actor.active_knowledge
    assert actor.disclosure['secret'] == 'concealed'


def test_diegetic_evidence_does_not_claim_runtime_truth():
    e = DiegeticEvidence('e1','testimony','X is dead','A',EvidenceReliability.UNKNOWN)
    assert e.claim == 'X is dead'
    assert e.reliability is EvidenceReliability.UNKNOWN


def test_productive_and_hard_contradictions_are_distinguished():
    assert classify_contradiction('canon') is ContradictionClass.CANON
    assert classify_contradiction('goal_conflict') is ContradictionClass.GOAL_CONFLICT
    assert classify_contradiction('relationship_paradox') is ContradictionClass.RELATIONSHIP_PARADOX


def test_candidate_same_basin_requires_structural_difference():
    a = CandidateConcept('A', CreativeSearchMode.EXPLORE, ('x',), 'same causal','same focal','same knowledge','same option','same rel','same reader')
    b = CandidateConcept('B', CreativeSearchMode.EXPLORE, ('x',), 'same causal','same focal','same knowledge','same option','same rel','same reader')
    c = CandidateConcept('C', CreativeSearchMode.REFRAME, ('goal_assumption',), 'different causal','same focal','different knowledge','different option','same rel','different reader')
    assert same_basin(a,b)
    assert not same_basin(a,c)


def test_winner_dominant_synthesis_keeps_one_causal_conception():
    winner = CandidateConcept('A', CreativeSearchMode.EXPLORE, ('x',), 'causal-A','focal-A','k-A','o-A','r-A','reader-A')
    alt = CandidateConcept('B', CreativeSearchMode.REFRAME, ('y',), 'causal-B','focal-B','k-B','o-B','r-B','reader-B')
    result = winner_dominant_synthesis(winner, [alt], bounded_contributions={'B':['useful constraint']})
    assert result.causal_premise == 'causal-A'
    assert result.contributions == ('useful constraint',)


def test_scene_metabolism_has_non_transformative_valid_modes():
    assert SceneMetabolism.INHABIT.value == 'INHABIT'
    assert SceneMetabolism.CONSOLIDATE.value == 'CONSOLIDATE'


def test_model_prior_audit_distinguishes_functional_repetition_from_formulaic_cross_context_repetition():
    from stateful_author.model_prior import BehaviorEvidence, BehaviorOwner
    evidence = BehaviorEvidence('REPETITION', BehaviorOwner.CHARACTER, ('span:1',), 'character-owned refrain')
    functional = audit_model_prior('가. 가. 가.', {'behavior_evidence': (evidence,)})
    assert 'FORMULAIC_REPETITION' not in functional
    formula = audit_model_prior('중요한 것은 A다. A가 아니라 B였다. 결국 B였다.', {})
    assert 'FORMULAIC_RHETORIC' in formula


def test_prepare_scene_and_commit_fail_closed_on_unqualified_proposal():
    contract = SceneContract('s1','A','write scene',(),(),(), 'NORMAL','v1', parent_state_hash=state_hash(STATE))
    prepared = prepare_scene(contract, STATE, LIB, scene_signals={})
    q = verify_proposal(prepared, text='x', context={'unreachable_claims': 1})
    assert q.qualification is QualificationStatus.FAIL
    from stateful_author.contracts import StateDelta
    with pytest.raises(ValueError, match='COMMIT_REQUIRES_PASS'):
        commit_verified(STATE, prepared, q, StateDelta(proposal_hash=q.proposal_hash))


def test_stale_parent_state_blocks_commit():
    contract = SceneContract('s1','A','write scene',(),(),(), 'NORMAL','v1', parent_state_hash=state_hash(STATE))
    prepared = prepare_scene(contract, STATE, LIB, scene_signals={})
    q = verify_proposal(prepared, text='x', context={})
    assert q.qualification is QualificationStatus.PASS
    stale_state = dict(STATE)
    stale_state['_version'] = 'v2'
    with pytest.raises(ValueError, match='STALE_PARENT_STATE'):
        from stateful_author.contracts import StateDelta
        commit_verified(stale_state, prepared, q, StateDelta(proposal_hash=q.proposal_hash))


def test_release_validator_rejects_stale_manifest_hash(tmp_path):
    # clean copied tree, corrupt the existing manifest only
    import shutil
    tree = tmp_path / 'tree'
    shutil.copytree(ROOT, tree)
    manifest_path = tree / 'RELEASE_MANIFEST.json'
    obj = json.loads(manifest_path.read_text(encoding='utf-8'))
    member = next(iter(obj['files']))
    obj['files'][member]['sha256'] = '0'*64
    manifest_path.write_text(json.dumps(obj), encoding='utf-8')
    result = validate_package(tree)
    assert any(x.startswith('MANIFEST_HASH_MISMATCH:') for x in result['errors'])


def test_release_validator_rejects_out_of_root_symlink(tmp_path):
    import shutil, os
    tree = tmp_path / 'tree'
    shutil.copytree(ROOT, tree)
    target = tmp_path / 'outside.txt'
    target.write_text('x')
    os.symlink(target, tree / 'stateful_author' / 'escape_link')
    result = validate_package(tree)
    assert any(x.startswith('OUT_OF_ROOT_SYMLINK:') for x in result['errors'])


def test_intelligence_rejects_unowned_effect_even_if_not_explicitly_forbidden():
    from stateful_author.verifier import verify_intelligence_usage
    failures = verify_intelligence_usage(
        [LIB['HUMOR_COGNITION']], {},
        {'HUMOR_COGNITION': {'world_weather': 'storm'}}, {}
    )
    assert 'INTELLIGENCE_UNOWNED_EFFECT:HUMOR_COGNITION:world_weather' in failures


def test_intelligence_rejects_effect_from_unselected_card():
    from stateful_author.verifier import verify_intelligence_usage
    failures = verify_intelligence_usage(
        [LIB['HUMOR_COGNITION']], {},
        {'REVEAL_CAUSAL_ACCOUNTING': {'causal_explanation': 'x'}}, {}
    )
    assert 'INTELLIGENCE_UNSELECTED_EFFECT:REVEAL_CAUSAL_ACCOUNTING' in failures


def test_intelligence_conflicting_shared_dimension_requires_resolver():
    from stateful_author.verifier import verify_intelligence_usage
    failures = verify_intelligence_usage(
        [LIB['PERCEPTION_SELECTION'], LIB['EMBODIMENT_AND_REALITY']], {},
        {
            'PERCEPTION_SELECTION': {'detail_selection': 'door'},
            'EMBODIMENT_AND_REALITY': {'detail_selection': 'blood'},
        }, {}
    )
    assert 'INTELLIGENCE_CONFLICT:detail_selection' in failures


def test_writer_packet_schema_is_executed_not_document_only():
    contract = SceneContract('s1','A','write',(),(),(), 'NORMAL','v1')
    packet = build_writer_packet(contract, STATE, [], LIB)
    assert 'scene' in packet and 'focal_now' in packet
    bad = SceneContract('s2','A','write',(),(),(), 'NORMAL','v1')
    # Huge strings are bounded before schema validation rather than leaking unlimited context.
    state = dict(STATE)
    state['event'] = {'visible_action': 'x' * 10000, 'hidden_note': 'SECRET'}
    packet2 = build_writer_packet(bad, state, [], LIB)
    assert len(packet2['world_now']['visible_action']) <= 4000
    assert 'hidden_note' not in packet2['world_now']


def test_grounded_major_reveal_is_not_rejected_merely_because_scene_is_also_domestic():
    from stateful_author.verifier import verify_intelligence_usage
    signals = {
        'ordinary_domestic': True,
        'major_reveal': SceneSignal('major_reveal', True, .95, ('e1',), SignalSource.TEXT_OBSERVED, 'HIGH'),
    }
    failures = verify_intelligence_usage([LIB['REVEAL_CAUSAL_ACCOUNTING']], signals, {}, {})
    assert 'INTELLIGENCE_OVERACTIVATION' not in failures


def test_pulled_context_is_not_a_mutable_alias_of_state():
    from stateful_author.intelligence import pull_card_context
    state = {
        'voice_state': {'attention_habits':['cost'], 'judgment_logic':['risk']},
        'narrative_state': {'knowledge': {'x': ['y']}, 'beliefs': {}},
        'relationship_state': {}
    }
    pulled = pull_card_context(LIB['CHARACTER_SPECIFIC_INTELLIGENCE'], state)
    pulled['narrative_state.knowledge']['x'].append('z')
    assert state['narrative_state']['knowledge']['x'] == ['y']


def test_strict_packet_collapses_duplicate_open_loop_source():
    contract = SceneContract('s','A','write',(),(),(), 'NORMAL','v1')
    state = dict(STATE)
    state['narrative_state'] = dict(STATE['narrative_state'])
    state['narrative_state']['open_loops'] = ['canonical_loop']
    state['open_loops'] = ['duplicate_legacy_loop']
    packet = build_writer_packet(contract, state, [], LIB)
    assert 'open_loops' not in packet
    assert 'narrative_state' not in packet
    assert 'duplicate_legacy_loop' not in repr(packet) and 'canonical_loop' not in repr(packet)


def test_verified_effect_must_belong_to_used_card():
    with pytest.raises(ValueError, match='RECEIPT_EFFECT_NOT_USED'):
        make_scene_receipt(
            scene_id='s', verified=True, state_delta={}, proposed_voice_delta={},
            intelligence_cards_used=['HUMOR_COGNITION'],
            intelligence_effects_verified=['REVEAL_CAUSAL_ACCOUNTING'],
        )


def test_unknown_failure_is_not_under_scoped_to_paragraph():
    from stateful_author.failure_router import repair_scope
    assert repair_scope('SOMETHING_NEW', 1) == 'SCENE'


def test_external_verification_observation_requires_typed_evidence():
    from stateful_author.verifier import VerificationEvidence, verify_external_evidence
    good = VerificationEvidence('e1','KNOWLEDGE_REACHABILITY',True,'TEXT_OBSERVED',.95, ('span:1',))
    assert verify_external_evidence([good]) == []
    weak = VerificationEvidence('e2','KNOWLEDGE_REACHABILITY',True,'DERIVED',.2)
    assert 'EXTERNAL_EVIDENCE_INSUFFICIENT:e2' in verify_external_evidence([weak])
