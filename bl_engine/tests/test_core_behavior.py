from stateful_author.surface import evaluate_paragraph_topology
from stateful_author.voice import VoiceState, VoiceCheckpoint, evaluate_voice_checkpoint, portable_line_risk
from stateful_author.provenance import EvidenceType, FactRecord, select_writer_facts
from stateful_author.cognition import route_cognition
from stateful_author.ownership import validate_overlay
from stateful_author.packet import compile_writer_packet
from stateful_author.receipt import make_scene_receipt
from stateful_author.failure_router import repair_scope


def test_stair_step_narration_fails_but_short_syntax_in_one_paragraph_passes():
    bad = "비가 왔다.\n\n문을 닫았다.\n\n손이 떨렸다.\n\n그는 기다렸다."
    good = "비가 왔다. 문을 닫았다. 손이 떨렸다. 그래도 그는 기다렸다."
    assert "PARAGRAPH_FRAGMENTATION" in evaluate_paragraph_topology(bad)
    assert evaluate_paragraph_topology(good) == []


def test_one_earned_isolated_line_is_allowed():
    text = "그는 한참 계산기를 두드렸다. 잔액은 변하지 않았다.\n\n끝이었다.\n\n다시 영수증을 접어 주머니에 넣었다."
    assert "PARAGRAPH_FRAGMENTATION" not in evaluate_paragraph_topology(text)


def test_pressure_can_remove_humor_without_erasing_voice_identity():
    base = VoiceState(
        attention_habits={"practical_cost", "body_signal"},
        judgment_logic={"usable_or_not"},
        reality_anchors={"money", "distance", "body"},
        emotional_evasion={"task_focus"},
        humor_mechanisms={"banal_collision"},
    )
    cp = VoiceCheckpoint(
        attention_habits={"body_signal"},
        judgment_logic={"usable_or_not"},
        reality_anchors={"distance", "body"},
        emotional_evasion={"task_focus"},
        humor_mechanisms=set(),
        pressure="HIGH",
    )
    assert evaluate_voice_checkpoint(base, cp) == []


def test_high_pressure_identity_erasure_fails():
    base = VoiceState(
        attention_habits={"practical_cost"}, judgment_logic={"usable_or_not"},
        reality_anchors={"money", "body"}, emotional_evasion={"task_focus"},
        humor_mechanisms={"banal_collision"},
    )
    cp = VoiceCheckpoint(set(), set(), set(), set(), set(), "HIGH", generic_narrator=True)
    failures = evaluate_voice_checkpoint(base, cp)
    assert "VOICE_DRIFT" in failures
    assert "REALITY_ANCHOR_LOSS" in failures


def test_portable_emotional_line_is_flagged_when_contextless():
    assert portable_line_risk("모든 것이 이미 끝나 버린 것 같았다.", context_tokens=set()) is True
    assert portable_line_risk("수리비 견적서를 접자 손가락에 기름이 묻었다.", context_tokens={"수리비", "견적서", "기름"}) is False


def test_hypothesis_does_not_become_writer_fact():
    facts = [
        FactRecord("job", "mechanic", EvidenceType.USER_CANON, 1.0),
        FactRecord("hates_people", True, EvidenceType.WORKING_HYPOTHESIS, 0.6),
    ]
    selected = select_writer_facts(facts)
    assert selected == {"job": "mechanic"}


def test_optional_cognition_router_can_return_nothing_for_everyday_scene():
    assert route_cognition({"everyday": True}) == set()
    assert route_cognition({"flashback": True}) == {"memory_relevance"}
    assert "closure_target" not in route_cognition({"reveal": True})


def test_source_dimension_ownership_blocks_story_engine_from_prose_surface():
    failures = validate_overlay("STORY_ARCHITECTURE", {"paragraph_topology": "one_line", "plot_pressure": "raise"})
    assert failures == ["SOURCE_BOUNDARY_LEAK:paragraph_topology"]


def test_writer_packet_strips_meta_and_source_material_recursively():
    packet = compile_writer_packet({
        "event": {"action": "enter"},
        "voice_state": {"attention_habits": ["cost"]},
        "narrative_state": {"facts": {"door": "locked"}, "closure_target": "shock"},
        "author_analysis": {"source_author": "SHOULD_NOT_LEAK"},
        "verification": {"failure_codes": ["VOICE_DRIFT"]},
        "serial_pressure": {"causal": 2},
    })
    flat = repr(packet)
    assert "SHOULD_NOT_LEAK" not in flat
    assert "VOICE_DRIFT" not in flat
    assert "closure_target" not in flat
    assert packet["event"]["action"] == "enter"


def test_failed_scene_cannot_mutate_durable_voice_state():
    receipt = make_scene_receipt(
        scene_id="s1", verified=False, state_delta={"door": "open"},
        proposed_voice_delta={"paragraph_behavior": "stair_step"}
    )
    assert receipt.voice_candidate_delta == {}
    assert receipt.committed_delta == {}
    assert receipt.candidate_delta['door'] == 'open'


def test_repeated_failure_escalates_to_architecture_not_more_line_polish():
    assert repair_scope("VOICE_DRIFT", repeat_count=1) == "SCENE"
    assert repair_scope("VOICE_DRIFT", repeat_count=2) == "VOICE_STATE"
    assert repair_scope("VOICE_DRIFT", repeat_count=3) == "ARCHITECTURE"
