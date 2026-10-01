from pathlib import Path
from stateful_author.intelligence import load_intelligence_library, evaluate_intelligence_sequence
from stateful_author.verifier import verify_intelligence_usage
from stateful_author.packet import compile_writer_packet

LIB = load_intelligence_library(Path('author/intelligence/cards'))
STATE = {
    'voice_state': {
        'attention_habits': ['cost', 'body'],
        'judgment_logic': ['usable_or_not'],
        'emotional_evasion': ['task_focus'],
        'reality_anchors': ['money', 'body'],
        'humor_mechanisms': ['banal_collision'],
    },
    'narrative_state': {'knowledge': {'door': 'locked'}, 'beliefs': {'visitor': 'late'}},
    'relationship_state': {'distance': 'guarded'},
    'open_loops': ['missing_key'],
    'relevant_recurrences': {'key': {'original': 'tool'}},
}


def test_long_horizon_activation_changes_by_need_and_does_not_accumulate():
    sequence = [
        {'ordinary_domestic': True},
        {'relationship_pivot': True},
        {'mystery_evidence_conflict': True},
        {'flashback': True},
        {'high_pressure': True},
        {'major_reveal': True},
        {'emotional_pressure': True},
        {'ordinary_domestic': True},
    ]
    result = evaluate_intelligence_sequence(sequence, STATE, LIB)
    assert 'RELATIONSHIP_EVIDENCE' in result.activations[1]
    assert 'INFORMATION_MODE_SELECTION' in result.activations[2]
    assert 'MEMORY_PRESENT_RELEVANCE' in result.activations[3]
    assert 'PRESSURE_RESPONSE' in result.activations[4]
    assert 'REVEAL_CAUSAL_ACCOUNTING' in result.activations[5]
    assert result.activations[-1] == ()
    assert result.failures == []


def test_reveal_card_in_mundane_scene_is_overactivation():
    failures = verify_intelligence_usage([LIB['REVEAL_CAUSAL_ACCOUNTING']], {'ordinary_domestic': True}, {}, {})
    assert 'INTELLIGENCE_OVERACTIVATION' in failures


def test_full_library_dump_is_detected_as_payload_bloat():
    packet = compile_writer_packet({'author_intelligence': [
        {'id': c.id, 'guidance': ['x'], 'trigger': c.trigger} for c in LIB.values()
    ]})
    failures = verify_intelligence_usage(list(LIB.values()), {}, {}, {'payload_bloat': len(packet.get('author_intelligence', [])) >= 8})
    assert 'INTELLIGENCE_PAYLOAD_BLOAT' in failures


def test_character_specific_intelligence_rejects_one_optimal_solution_for_everyone():
    failures = verify_intelligence_usage(
        [LIB['CHARACTER_SPECIFIC_INTELLIGENCE']], {'consequential_decision': True}, {},
        {'character_solution_diversity': 0}
    )
    assert 'CHARACTER_GENERICITY' in failures
