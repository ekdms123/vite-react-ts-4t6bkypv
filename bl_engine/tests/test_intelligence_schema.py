from pathlib import Path
import json
import pytest

from stateful_author.intelligence import IntelligenceCard, load_intelligence_library, validate_card

CARDS = Path('author/intelligence/cards')
EXPECTED = {
    'PERCEPTION_SELECTION', 'CHARACTER_SPECIFIC_INTELLIGENCE',
    'RELATIONSHIP_EVIDENCE', 'DIALOGUE_AS_RELATIONAL_ACTION',
    'EMOTIONAL_AVOIDANCE', 'EMBODIMENT_AND_REALITY',
    'HUMOR_COGNITION', 'INFORMATION_MODE_SELECTION',
    'MYSTERY_FAIRNESS', 'REVEAL_CAUSAL_ACCOUNTING',
    'RECURRENCE_RECODING', 'MEMORY_PRESENT_RELEVANCE',
    'PRESSURE_RESPONSE',
}


def test_all_13_selectable_cards_exist_and_validate():
    library = load_intelligence_library(CARDS)
    assert set(library) == EXPECTED
    assert all(validate_card(card) == [] for card in library.values())


def test_card_ownership_cannot_overlap_forbidden_dimensions():
    library = load_intelligence_library(CARDS)
    for card in library.values():
        assert not (set(card.owns_dimensions) & set(card.forbidden_dimensions))


def test_writer_cards_are_source_clean():
    blob = '\n'.join(p.read_text('utf-8') for p in CARDS.glob('*.json'))
    for forbidden in ['미친 여름', '첫 병', '마왕', '홍염의 연인', 'reason', '세디백']:
        assert forbidden not in blob


def test_validator_rejects_missing_required_field():
    card = IntelligenceCard(
        id='', version=1, purpose='x', trigger={}, preconditions=(),
        owns_dimensions=('attention_selection',), forbidden_dimensions=(),
        context_requirements={'required': [], 'optional': []},
        writer_payload={'max_items': 2, 'form': 'decision_guidance'},
        suppress_when=(), verifier_checks=(),
    )
    assert 'CARD_FIELD_MISSING:id' in validate_card(card)


def test_loader_rejects_duplicate_ids(tmp_path):
    manifest = {
        'id': 'DUP', 'version': 1, 'purpose': 'x', 'trigger': {'any': ['x']},
        'preconditions': [], 'owns_dimensions': ['attention_selection'],
        'forbidden_dimensions': [],
        'context_requirements': {'required': [], 'optional': []},
        'writer_payload': {'max_items': 2, 'form': 'decision_guidance'},
        'suppress_when': [], 'verifier_checks': [],
    }
    (tmp_path / 'a.json').write_text(json.dumps(manifest), encoding='utf-8')
    (tmp_path / 'b.json').write_text(json.dumps(manifest), encoding='utf-8')
    with pytest.raises(ValueError, match='duplicate card id'):
        load_intelligence_library(tmp_path)
