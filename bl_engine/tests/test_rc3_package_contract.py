from pathlib import Path
import shutil

from stateful_author.release import validate_package

ROOT = Path(__file__).resolve().parents[1]


def clone(tmp_path):
    out = tmp_path / 'candidate'
    shutil.copytree(ROOT, out, ignore=shutil.ignore_patterns('.pytest_cache', '__pycache__', 'RELEASE_MANIFEST.json'))
    return out


def test_validator_requires_intelligence_library(tmp_path):
    candidate = clone(tmp_path)
    shutil.rmtree(candidate / 'author/intelligence')
    result = validate_package(candidate)
    assert 'MISSING:author/intelligence/cards' in result['errors']


def test_validator_rejects_missing_selectable_card(tmp_path):
    candidate = clone(tmp_path)
    (candidate / 'author/intelligence/cards/REVEAL_CAUSAL_ACCOUNTING.json').unlink()
    result = validate_package(candidate)
    assert any(e.startswith('INTELLIGENCE_CARD_SET_MISMATCH:') for e in result['errors'])


def test_validator_rejects_writer_runtime_audit_vocabulary(tmp_path):
    candidate = clone(tmp_path)
    runtime = candidate / 'runtime/WRITER_RUNTIME.md'
    runtime.write_text(runtime.read_text(encoding='utf-8') + '\nMULTI_ALTITUDE_AUDIT\n', encoding='utf-8')
    result = validate_package(candidate)
    assert 'WRITER_RUNTIME_LEAK:MULTI_ALTITUDE_AUDIT' in result['errors']


def test_validator_rejects_nested_zip_input(tmp_path):
    candidate = clone(tmp_path)
    (candidate / 'input_archive.zip').write_bytes(b'not-a-real-zip')
    result = validate_package(candidate)
    assert 'FORBIDDEN_INPUT_ARTIFACT:input_archive.zip' in result['errors']


def test_validator_accepts_current_rc3_tree():
    result = validate_package(ROOT)
    assert result['errors'] == []
    assert result['warnings'] == []


def test_standalone_validator_tool_exists_and_accepts_current_tree():
    import subprocess, sys
    tool = ROOT / 'tools/validate_package.py'
    assert tool.is_file()
    run = subprocess.run([sys.executable, str(tool), str(ROOT)], text=True, capture_output=True)
    assert run.returncode == 0, run.stdout + run.stderr
    assert 'errors: 0' in run.stdout
    assert 'warnings: 0' in run.stdout
