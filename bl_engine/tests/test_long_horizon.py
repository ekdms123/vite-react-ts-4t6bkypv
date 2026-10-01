from stateful_author.voice import VoiceState, VoiceCheckpoint
from stateful_author.long_horizon import evaluate_long_horizon


def baseline():
    return VoiceState(
        attention_habits={"practical_cost", "body_signal", "exit_route"},
        judgment_logic={"usable_or_not", "risk_first"},
        reality_anchors={"money", "distance", "body", "objects"},
        emotional_evasion={"task_focus"},
        humor_mechanisms={"banal_collision"},
    )


def test_long_horizon_preserves_identity_across_pressure_memory_and_return():
    checkpoints = [
        VoiceCheckpoint({"practical_cost"}, {"usable_or_not"}, {"money", "objects"}, {"task_focus"}, {"banal_collision"}, "LOW"),
        VoiceCheckpoint({"body_signal", "exit_route"}, {"risk_first"}, {"distance", "body"}, {"task_focus"}, set(), "HIGH"),
        VoiceCheckpoint({"practical_cost", "body_signal"}, {"usable_or_not"}, {"objects", "body"}, {"task_focus"}, set(), "MEMORY", narrative_mode="EMBODIED_MEMORY"),
        VoiceCheckpoint({"practical_cost"}, {"usable_or_not"}, {"money", "objects"}, {"task_focus"}, {"banal_collision"}, "AFTERMATH"),
    ]
    result = evaluate_long_horizon(baseline(), checkpoints)
    assert result.failures == []
    assert result.vector["voice_continuity"] >= 0.8
    assert result.vector["reality_anchor_continuity"] >= 0.8


def test_late_generic_reversion_is_caught_even_if_early_checkpoints_are_good():
    checkpoints = [
        VoiceCheckpoint({"practical_cost"}, {"usable_or_not"}, {"money"}, {"task_focus"}, {"banal_collision"}, "LOW"),
        VoiceCheckpoint({"body_signal"}, {"risk_first"}, {"distance", "body"}, {"task_focus"}, set(), "HIGH"),
        VoiceCheckpoint(set(), set(), set(), set(), set(), "AFTERMATH", generic_narrator=True, paragraph_fragmentation=True),
    ]
    result = evaluate_long_horizon(baseline(), checkpoints)
    assert "LATE_VOICE_REVERSION" in result.failures
    assert "LONG_HORIZON_SURFACE_DRIFT" in result.failures


def test_biographical_memory_checkpoint_counts_as_long_horizon_mode_drift():
    checkpoints = [
        VoiceCheckpoint({"body_signal"}, {"risk_first"}, {"body"}, {"task_focus"}, set(), "MEMORY", narrative_mode="BIOGRAPHICAL_SUMMARY"),
    ]
    result = evaluate_long_horizon(baseline(), checkpoints)
    assert "LONG_HORIZON_MEMORY_DRIFT" in result.failures
