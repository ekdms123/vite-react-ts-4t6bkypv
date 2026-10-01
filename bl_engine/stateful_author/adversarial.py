from pathlib import Path

from .surface import evaluate_paragraph_topology
from .ownership import validate_overlay
from .verifier import verify_scene, verify_intelligence_usage
from .serial import EpisodeDelta, PressureVector
from .commercial import evaluate_commercial_arc
from .intelligence import load_intelligence_library


def _library():
    root = Path(__file__).resolve().parents[1]
    return load_intelligence_library(root / 'author/intelligence/cards')


def run_adversarial_audit() -> dict[str, list[str]]:
    report: dict[str, list[str]] = {}
    report['STAIR_STEP_ATTACK'] = evaluate_paragraph_topology('비가 왔다.\n\n문을 닫았다.\n\n숨을 삼켰다.\n\n기다렸다.')
    report['STORY_PROSE_LEAK_ATTACK'] = validate_overlay('STORY_ARCHITECTURE', {'paragraph_topology':'one_line'})
    report['MEMORY_BIOGRAPHY_ATTACK'] = verify_scene('열 살에 떠났고 스무 살에 돌아왔다.', {'mode':'MEMORY','chronology_summary_ratio':0.9,'present_relevance':False}).failures
    report['GENERIC_PRIOR_ATTACK'] = verify_scene('모든 것이 끝났고 운명이 문을 열었다.', {'generic_emotional_line':True,'abstract_story_metaphor':True,'reality_anchor_count':0}).failures
    report['CLOSURE_STACK_ATTACK'] = verify_scene('끝이었다. 정말 끝났다. 돌아갈 수 없었다.', {'terminal_beats':3,'post_terminal_state_delta':False}).failures
    report['SOURCE_RESIDUE_ATTACK'] = verify_scene('SOURCE_SIGNATURE_X', {'restricted_source_tokens':{'SOURCE_SIGNATURE_X'}}).failures
    eps = [{'delta':EpisodeDelta(cliffhanger_only=True),'pressure':PressureVector(information=3)} for _ in range(4)]
    report['SERIAL_CLIFFHANGER_ATTACK'] = evaluate_commercial_arc(eps, []).failures

    lib = _library()
    all_cards = list(lib.values())
    report['INTELLIGENCE_ALL_ON_ATTACK'] = verify_intelligence_usage(
        all_cards, {'ordinary_domestic': True}, {}, {}
    )
    report['INTELLIGENCE_REVEAL_MUNDANE_ATTACK'] = verify_intelligence_usage(
        [lib['REVEAL_CAUSAL_ACCOUNTING']], {'ordinary_domestic': True}, {}, {}
    )
    report['INTELLIGENCE_HUMOR_SURFACE_ATTACK'] = verify_intelligence_usage(
        [lib['HUMOR_COGNITION']], {},
        {'HUMOR_COGNITION': {'paragraph_topology': 'fragmented'}}, {}
    )
    report['INTELLIGENCE_MISDIRECTION_NO_VALUE_ATTACK'] = verify_intelligence_usage(
        [lib['INFORMATION_MODE_SELECTION'], lib['MYSTERY_FAIRNESS']],
        {'active_misdirection': True}, {}, {'misdirection_causal_gain': False}
    )
    report['INTELLIGENCE_RECURRENCE_NO_RECODING_ATTACK'] = verify_intelligence_usage(
        [lib['RECURRENCE_RECODING']], {'recurrence_return': True}, {},
        {'recurrence_emphasized': True, 'recurrence_recoded': False}
    )
    report['INTELLIGENCE_LIBRARY_DUMP_ATTACK'] = verify_intelligence_usage(
        all_cards, {}, {}, {'payload_bloat': True}
    )
    report['INTELLIGENCE_CHARACTER_GENERICITY_ATTACK'] = verify_intelligence_usage(
        [lib['CHARACTER_SPECIFIC_INTELLIGENCE']], {'consequential_decision': True}, {},
        {'character_solution_diversity': 0}
    )
    return report
