from stateful_author.serial import EpisodeDelta, PressureVector, QuestionTransformation
from stateful_author.commercial import evaluate_commercial_arc


def test_compounding_arc_passes_without_requiring_cliffhanger_every_episode():
    episodes = [
        {"delta": EpisodeDelta(fact_changes={"key_found"}), "pressure": PressureVector(information=2, desire=1)},
        {"delta": EpisodeDelta(relationship_changes={"A-B:access+1"}), "pressure": PressureVector(relationship=2, plan=1)},
        {"delta": EpisodeDelta(belief_changes={"suspect_model_false"}), "pressure": PressureVector(information=3, causal=1)},
        {"delta": EpisodeDelta(consequence_changes={"safehouse_lost"}), "pressure": PressureVector(causal=3, world=2)},
        {"delta": EpisodeDelta(relationship_changes={"A-B:trust+1"}), "pressure": PressureVector(emotional_afterpressure=2)},
    ]
    transformations = [QuestionTransformation(
        "Who took the key?", "The ally moved it", "The move protected someone else",
        "Who was the ally protecting?", True, True
    )]
    result = evaluate_commercial_arc(episodes, transformations)
    assert result.failures == []
    assert result.vector["episode_delta_coverage"] == 1.0
    assert result.vector["pressure_diversity"] >= 0.5
    assert result.vector["question_transformation"] == 1.0


def test_repeated_cliffhanger_without_delta_is_serial_stagnation():
    episodes = [
        {"delta": EpisodeDelta(cliffhanger_only=True), "pressure": PressureVector(information=3)},
        {"delta": EpisodeDelta(cliffhanger_only=True), "pressure": PressureVector(information=3)},
        {"delta": EpisodeDelta(cliffhanger_only=True), "pressure": PressureVector(information=3)},
        {"delta": EpisodeDelta(cliffhanger_only=True), "pressure": PressureVector(information=3)},
    ]
    result = evaluate_commercial_arc(episodes, [])
    assert "SERIAL_STAGNATION" in result.failures
    assert "FALSE_PROGRESS" in result.failures


def test_arc_vector_is_multidimensional_not_single_good_score():
    result = evaluate_commercial_arc([
        {"delta": EpisodeDelta(fact_changes={"x"}), "pressure": PressureVector(causal=1)}
    ], [])
    assert set(result.vector) >= {"episode_delta_coverage", "pressure_diversity", "relationship_productivity", "question_transformation", "causal_compounding"}
    assert "overall_score" not in result.vector
