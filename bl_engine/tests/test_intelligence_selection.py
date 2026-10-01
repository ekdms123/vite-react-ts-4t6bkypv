from pathlib import Path
import pytest
from stateful_author.intelligence import (
    load_intelligence_library, select_intelligence_cards,
    pull_card_context, compile_intelligence_payload,
)

@pytest.fixture
def library():
    return load_intelligence_library(Path('author/intelligence/cards'))

BASE_STATE = {
    'voice_state': {
        'attention_habits': ['cost', 'body'],
        'judgment_logic': ['usable_or_not'],
        'emotional_evasion': ['task_focus'],
        'reality_anchors': ['money', 'body', 'tools'],
        'humor_mechanisms': ['banal_collision'],
    },
    'narrative_state': {'knowledge': {'door': 'locked'}, 'beliefs': {'visitor': 'late'}},
    'relationship_state': {'distance': 'guarded'},
    'open_loops': ['missing_key'],
    'relevant_recurrences': {'red_receipt': {'original': 'debt reminder'}},
}

def ids(cards):
    return {c.id for c in cards}


def test_domestic_scene_does_not_retrieve_reveal_or_misdirection(library):
    selected = ids(select_intelligence_cards({'ordinary_domestic': True}, BASE_STATE, library))
    assert 'REVEAL_CAUSAL_ACCOUNTING' not in selected
    assert 'MYSTERY_FAIRNESS' not in selected
    assert 'INFORMATION_MODE_SELECTION' not in selected


def test_major_reveal_retrieves_reveal_accounting(library):
    selected = ids(select_intelligence_cards({'major_reveal': True}, BASE_STATE, library))
    assert 'REVEAL_CAUSAL_ACCOUNTING' in selected


def test_relationship_pivot_retrieves_relationship_and_dialogue_action(library):
    selected = ids(select_intelligence_cards({'relationship_pivot': True}, BASE_STATE, library))
    assert {'RELATIONSHIP_EVIDENCE', 'DIALOGUE_AS_RELATIONAL_ACTION'} <= selected


def test_high_pressure_retrieves_pressure_response_without_forcing_humor(library):
    selected = ids(select_intelligence_cards({'high_pressure': True}, BASE_STATE, library))
    assert 'PRESSURE_RESPONSE' in selected
    assert 'HUMOR_COGNITION' not in selected


def test_unchanged_recurrence_suppresses_recurrence_card(library):
    selected = ids(select_intelligence_cards({'recurrence_return': True, 'recurrence_unchanged': True}, BASE_STATE, library))
    assert 'RECURRENCE_RECODING' not in selected


def test_recoded_recurrence_selects_recurrence_card(library):
    selected = ids(select_intelligence_cards({'recurrence_return': True, 'recurrence_recoded': True}, BASE_STATE, library))
    assert 'RECURRENCE_RECODING' in selected


def test_memory_without_present_consequence_suppresses_memory_expansion(library):
    selected = ids(select_intelligence_cards({'flashback': True, 'no_present_consequence': True}, BASE_STATE, library))
    assert 'MEMORY_PRESENT_RELEVANCE' not in selected


def test_consequential_problem_selects_character_specific_intelligence(library):
    selected = ids(select_intelligence_cards({'consequential_decision': True}, BASE_STATE, library))
    assert 'CHARACTER_SPECIFIC_INTELLIGENCE' in selected


def test_required_context_missing_suppresses_card(library):
    selected = ids(select_intelligence_cards({'consequential_decision': True}, {'voice_state': {}}, library))
    assert 'CHARACTER_SPECIFIC_INTELLIGENCE' not in selected


def test_context_pull_reads_only_declared_paths(library):
    card = library['CHARACTER_SPECIFIC_INTELLIGENCE']
    pulled = pull_card_context(card, BASE_STATE)
    assert set(pulled) <= {
        'voice_state.attention_habits', 'voice_state.judgment_logic',
        'narrative_state.knowledge', 'narrative_state.beliefs', 'relationship_state'
    }
    assert 'open_loops' not in pulled


def test_compiled_payload_is_small_and_manifest_free(library):
    card = library['REVEAL_CAUSAL_ACCOUNTING']
    context = pull_card_context(card, BASE_STATE)
    payload = compile_intelligence_payload(card, context, {'major_reveal': True})
    assert set(payload) == {'id', 'guidance'}
    assert payload['id'] == 'REVEAL_CAUSAL_ACCOUNTING'
    assert 1 <= len(payload['guidance']) <= card.writer_payload['max_items']
    flat = repr(payload)
    for forbidden in ['trigger', 'forbidden_dimensions', 'verifier_checks', 'source_author']:
        assert forbidden not in flat
