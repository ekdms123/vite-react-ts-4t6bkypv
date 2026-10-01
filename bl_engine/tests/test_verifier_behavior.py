from stateful_author.verifier import verify_scene


def test_generic_dramatic_cluster_triggers_model_prior_reversion_but_single_phrase_does_not():
    single = verify_scene("끝난 것 같았다.", {"context_tokens": {"receipt"}})
    cluster = verify_scene(
        "모든 것이 끝난 것 같았다. 이미 무언가가 시작된 것처럼 운명은 문을 열고 있었다.",
        {"context_tokens": set(), "generic_emotional_line": True, "abstract_story_metaphor": True, "reality_anchor_count": 0}
    )
    assert "MODEL_PRIOR_REVERSION" not in single.failures
    assert "MODEL_PRIOR_REVERSION" in cluster.failures


def test_memory_biography_drift_is_detected():
    result = verify_scene("그는 열 살에 떠났고 열다섯에 돌아왔으며 스무 살에 다시 떠났다.", {
        "mode": "MEMORY", "chronology_summary_ratio": 0.85, "present_relevance": False,
    })
    assert "NARRATIVE_MODE_DRIFT" in result.failures


def test_closure_stacking_detects_multiple_terminal_beats_without_new_state():
    result = verify_scene("끝이었다. 이제 정말 끝났다. 돌아갈 수 없었다.", {"terminal_beats": 3, "post_terminal_state_delta": False})
    assert "CLOSURE_STACKING" in result.failures


def test_redundant_meaning_recovery_detects_repeated_explanation():
    result = verify_scene("그는 가지 않았다. 결국 떠나지 않은 것이다. 남았다는 뜻이었다.", {"meaning_recovery_count": 3})
    assert "REDUNDANT_MEANING_RECOVERY" in result.failures


def test_knowledge_leak_and_source_residue_are_separate_failures():
    result = verify_scene("그녀는 속으로 이미 결심했다. SOURCE_SIGNATURE_X", {
        "unreachable_claims": 1, "restricted_source_tokens": {"SOURCE_SIGNATURE_X"}
    })
    assert "KNOWLEDGE_LEAK" in result.failures
    assert "SOURCE_RESIDUE" in result.failures
