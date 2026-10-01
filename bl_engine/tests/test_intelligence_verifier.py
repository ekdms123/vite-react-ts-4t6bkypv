from pathlib import Path
from stateful_author.intelligence import load_intelligence_library
from stateful_author.verifier import verify_intelligence_usage
from stateful_author.receipt import make_scene_receipt

LIB = load_intelligence_library(Path('author/intelligence/cards'))


def test_humor_card_cannot_change_paragraph_topology():
    failures = verify_intelligence_usage(
        [LIB['HUMOR_COGNITION']], {},
        {'HUMOR_COGNITION': {'paragraph_topology': 'fragmented'}}, {}
    )
    assert 'INTELLIGENCE_DIMENSION_LEAK:HUMOR_COGNITION:paragraph_topology' in failures


def test_reveal_card_cannot_raise_narrator_register():
    failures = verify_intelligence_usage(
        [LIB['REVEAL_CAUSAL_ACCOUNTING']], {'major_reveal': True},
        {'REVEAL_CAUSAL_ACCOUNTING': {'narrator_register': 'grand'}}, {}
    )
    assert 'INTELLIGENCE_DIMENSION_LEAK:REVEAL_CAUSAL_ACCOUNTING:narrator_register' in failures


def test_relationship_card_cannot_invent_unreachable_knowledge():
    failures = verify_intelligence_usage(
        [LIB['RELATIONSHIP_EVIDENCE']], {'relationship_pivot': True},
        {'RELATIONSHIP_EVIDENCE': {'speaker_knowledge': 'secret'}}, {'unreachable_claims': 1}
    )
    assert 'KNOWLEDGE_LEAK' in failures


def test_every_card_active_in_mundane_scene_is_overactivation():
    failures = verify_intelligence_usage(list(LIB.values()), {'ordinary_domestic': True}, {}, {})
    assert 'INTELLIGENCE_OVERACTIVATION' in failures


def test_active_misdirection_without_causal_gain_fails():
    failures = verify_intelligence_usage(
        [LIB['INFORMATION_MODE_SELECTION'], LIB['MYSTERY_FAIRNESS']],
        {'active_misdirection': True}, {}, {'misdirection_causal_gain': False}
    )
    assert 'MISDIRECTION_WITHOUT_VALUE' in failures


def test_emphasized_recurrence_without_recoding_fails():
    failures = verify_intelligence_usage(
        [LIB['RECURRENCE_RECODING']], {'recurrence_return': True}, {},
        {'recurrence_emphasized': True, 'recurrence_recoded': False}
    )
    assert 'RECURRENCE_WITHOUT_RECODING' in failures


def test_missing_material_card_can_be_reported_as_underretrieval():
    failures = verify_intelligence_usage([], {'major_reveal': True}, {}, {'material_missing_card': 'REVEAL_CAUSAL_ACCOUNTING'})
    assert 'INTELLIGENCE_UNDERRETRIEVAL:REVEAL_CAUSAL_ACCOUNTING' in failures


def test_receipt_records_card_effects_but_not_raw_prose():
    receipt = make_scene_receipt(
        scene_id='s1', verified=True, state_delta={'door': 'open'}, proposed_voice_delta={},
        intelligence_cards_used=['RELATIONSHIP_EVIDENCE'],
        intelligence_effects_verified=['RELATIONSHIP_EVIDENCE'],
        intelligence_effects_rejected=['HUMOR_COGNITION'],
    )
    assert receipt.intelligence_cards_used == ('RELATIONSHIP_EVIDENCE',)
    assert receipt.intelligence_effects_verified == ('RELATIONSHIP_EVIDENCE',)
    assert receipt.intelligence_effects_rejected == ('HUMOR_COGNITION',)
    assert not hasattr(receipt, 'raw_prose')


def test_failed_scene_does_not_promote_intelligence_generated_voice_delta():
    receipt = make_scene_receipt(
        scene_id='s2', verified=False, state_delta={},
        proposed_voice_delta={'new_behavior': 'generic_grandeur'},
        intelligence_cards_used=['REVEAL_CAUSAL_ACCOUNTING'],
        intelligence_effects_rejected=['REVEAL_CAUSAL_ACCOUNTING'],
    )
    assert receipt.voice_candidate_delta == {}


def test_rc3_failure_taxonomy_is_declared_in_verification_gate():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    gate = json.loads((root / 'verify/VERIFICATION_GATE.json').read_text(encoding='utf-8'))
    declared = set(gate['failure_taxonomy'])
    assert {
        'INTELLIGENCE_OVERACTIVATION', 'INTELLIGENCE_UNDERRETRIEVAL',
        'INTELLIGENCE_DIMENSION_LEAK', 'INTELLIGENCE_PAYLOAD_BLOAT',
        'MISDIRECTION_WITHOUT_VALUE', 'RECURRENCE_WITHOUT_RECODING',
        'CHARACTER_GENERICITY',
    } <= declared
