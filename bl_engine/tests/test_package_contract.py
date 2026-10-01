import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_runtime_and_analysis_artifacts_exist():
    required = [
        "START_HERE.md", "KERNEL_CONTRACT.md", "README.md",
        "author_analysis/SOURCE_REGISTRY.json", "author_analysis/HOLDOUT_MANIFEST.json",
        "author/SOURCE_DIMENSION_OWNERSHIP.json", "author/CANONICAL_SYNTHETIC_AUTHOR.md",
        "state/VOICE_CONTINUITY_SCHEMA.json", "state/NARRATIVE_STATE_SCHEMA.json", "state/SCENE_RECEIPT_SCHEMA.json",
        "runtime/WRITER_RUNTIME.md", "runtime/WRITER_PACKET_SCHEMA.json",
        "verify/VERIFICATION_GATE.json", "VERIFICATION_REPORT.md",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    assert missing == []


def test_writer_runtime_does_not_contain_source_author_names_or_failure_codes():
    text = (ROOT / "runtime/WRITER_RUNTIME.md").read_text(encoding="utf-8")
    forbidden = ["미친 여름", "첫 병", "마왕", "홍염의 연인", "VOICE_DRIFT", "MODEL_PRIOR_REVERSION", "closure_target"]
    assert [x for x in forbidden if x in text] == []


def test_source_ownership_has_explicit_non_authority_boundaries():
    obj = json.loads((ROOT / "author/SOURCE_DIMENSION_OWNERSHIP.json").read_text(encoding="utf-8"))
    assert "paragraph_topology" in obj["HUMOR_COGNITION"]["forbidden_to_modify"]
    assert "paragraph_topology" in obj["STORY_ARCHITECTURE"]["forbidden_to_modify"]
    assert "pov_distance" in obj["STORY_ARCHITECTURE"]["forbidden_to_modify"]
