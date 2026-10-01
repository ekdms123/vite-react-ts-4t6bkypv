from pathlib import Path
import json, zipfile
from stateful_author.release import validate_package, build_release

ROOT = Path(__file__).resolve().parents[1]


def test_package_validator_reports_no_errors_for_candidate_tree():
    result = validate_package(ROOT)
    assert result["errors"] == []
    assert result["warnings"] == []


def test_release_zip_contains_runtime_contracts_but_not_source_corpus(tmp_path):
    out = tmp_path / "runtime.zip"
    result = build_release(ROOT, out)
    assert result["zip_path"] == str(out)
    with zipfile.ZipFile(out) as z:
        names = set(z.namelist())
    assert "runtime/WRITER_RUNTIME.md" in names
    assert "author/SOURCE_DIMENSION_OWNERSHIP.json" in names
    assert "RELEASE_MANIFEST.json" in names
    assert not any(name.endswith((".pdf", ".txt")) for name in names)


def test_release_manifest_hashes_packaged_files(tmp_path):
    out = tmp_path / "runtime.zip"
    build_release(ROOT, out)
    with zipfile.ZipFile(out) as z:
        manifest = json.loads(z.read("RELEASE_MANIFEST.json"))
        member = "runtime/WRITER_RUNTIME.md"
        assert member in manifest["files"]
        assert len(manifest["files"][member]["sha256"]) == 64


def test_rc3_release_manifest_and_intelligence_library_are_packaged(tmp_path):
    out = tmp_path / 'rc3.zip'
    build_release(ROOT, out)
    with zipfile.ZipFile(out) as z:
        names = set(z.namelist())
        manifest = json.loads(z.read('RELEASE_MANIFEST.json'))
    assert manifest['release'] == (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    assert 'author/intelligence/cards/REVEAL_CAUSAL_ACCOUNTING.json' in names
    assert 'author/intelligence/VERIFIER_AUDITS.md' in names
    assert 'tools/validate_package.py' in names
