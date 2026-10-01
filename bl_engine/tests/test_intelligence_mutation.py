from pathlib import Path
import json
from stateful_author.intelligence import load_intelligence_library, select_intelligence_cards

ROOT = Path(__file__).resolve().parents[1]
LIB = load_intelligence_library(ROOT / 'author/intelligence/cards')
STATE = {
    'voice_state': {
        'attention_habits': ['cost'], 'judgment_logic': ['usable_or_not'],
        'emotional_evasion': ['task_focus'], 'reality_anchors': ['body'],
    },
    'narrative_state': {'knowledge': {}, 'beliefs': {}},
    'relationship_state': {'distance': 'guarded'},
}


def test_expected_card_fixtures_match_real_selector_output():
    cases = json.loads((ROOT / 'tests/fixtures/intelligence_selection_cases.json').read_text(encoding='utf-8'))
    for case in cases:
        actual = {card.id for card in select_intelligence_cards(case['signals'], STATE, LIB)}
        assert actual == set(case['expected_cards']), case['name']
