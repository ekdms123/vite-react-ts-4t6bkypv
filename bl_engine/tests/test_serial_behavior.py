from stateful_author.serial import (
    EpisodeDelta, PressureVector, QuestionTransformation,
    CharacterBehavioralPromise, evaluate_character_promise,
    relationship_productive,
)


def test_quiet_relationship_change_counts_as_episode_progress():
    d = EpisodeDelta(relationship_changes={"A-B:trust+1"})
    assert d.has_progress()


def test_fake_cliffhanger_without_state_delta_is_not_progress():
    d = EpisodeDelta(cliffhanger_only=True)
    assert not d.has_progress()


def test_pressure_is_vector_not_single_commercial_score():
    p = PressureVector(causal=1, information=2, relationship=3, desire=0, plan=1, identity=0, world=0, emotional_afterpressure=1)
    assert p.active_dimensions() == {"causal", "information", "relationship", "plan", "emotional_afterpressure"}
    assert not hasattr(p, "commercial_score")


def test_question_transformation_requires_reinterpretation_and_causal_link():
    good = QuestionTransformation(
        old_question="Who sent it?", partial_answer="A courier",
        reinterpretation="The courier was bait", new_question="Who wanted the courier followed?",
        causal_link=True, recoded_prior_evidence=True,
    )
    bad = QuestionTransformation(
        old_question="Who sent it?", partial_answer="A courier",
        reinterpretation="", new_question="What is in the box?",
        causal_link=False, recoded_prior_evidence=False,
    )
    assert good.is_valid()
    assert not bad.is_valid()


def test_character_promise_allows_variation_but_requires_trigger_for_core_violation():
    promise = CharacterBehavioralPromise(
        stable_core={"protects_younger"}, predictable_tendency={"avoids_authority"},
        contradiction={"wants_approval"}, violation_triggers={"younger_betrayal"}
    )
    assert evaluate_character_promise(promise, action_tags={"protects_younger"}, active_triggers=set()) == []
    assert "UNMOTIVATED_PROMISE_BREAK" in evaluate_character_promise(promise, action_tags={"abandons_younger"}, active_triggers=set())
    assert evaluate_character_promise(promise, action_tags={"abandons_younger"}, active_triggers={"younger_betrayal"}) == []


def test_relationship_productivity_requires_changed_access_boundary_risk_or_attention():
    assert relationship_productive({"evidence": ["waited_outside"], "boundary_change": True})
    assert not relationship_productive({"banter": True})
