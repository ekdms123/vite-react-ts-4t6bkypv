from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_has_only_declared_core_layers():
    allowed = {
        'voice', 'author_analysis', 'author', 'state', 'cognition', 'serial', 'runtime',
        'verify', 'stateful_author', 'tests', 'baseline', 'tools', 'docs', 'vendor'
    }
    actual = {p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith('.') and p.name != 'dist'}
    assert actual <= allowed


def test_core_runtime_docs_are_medium_independent():
    targets = [
        ROOT / 'KERNEL_CONTRACT.md',
        ROOT / 'runtime/WRITER_RUNTIME.md',
        ROOT / 'author_analysis/CROSS_AUTHOR_MAP.md',
        ROOT / 'VERIFICATION_REPORT.md',
    ]
    forbidden = ['adapter-specific production rules inside the writer']
    leaks = []
    for path in targets:
        text = path.read_text(encoding='utf-8').lower()
        for token in forbidden:
            if token.lower() in text:
                leaks.append(f'{path.relative_to(ROOT)}:{token}')
    assert leaks == []


def test_scene_receipt_is_not_media_specific():
    schema = json.loads((ROOT / 'state/SCENE_RECEIPT_SCHEMA.json').read_text(encoding='utf-8'))
    props = schema.get('properties', {})
    assert 'visual_delta' not in props
    assert 'panel_delta' not in props
    assert 'adapter_delta' not in props


def test_verification_gate_has_no_medium_specific_level():
    gate = json.loads((ROOT / 'verify/VERIFICATION_GATE.json').read_text(encoding='utf-8'))
    levels = set(gate.get('levels', []))
    assert 'ADAPTATION_LAYER' not in levels


def test_release_validator_rejects_undeclared_production_layer(tmp_path):
    import shutil
    from stateful_author.release import validate_package
    candidate = tmp_path / 'candidate'
    shutil.copytree(ROOT, candidate, ignore=shutil.ignore_patterns('.pytest_cache', '__pycache__', 'RELEASE_MANIFEST.json'))
    extra = candidate / 'medium_adapter'
    extra.mkdir()
    (extra / 'RULES.md').write_text('adapter-specific production rules', encoding='utf-8')
    result = validate_package(candidate)
    assert 'UNDECLARED_LAYER:medium_adapter' in result['errors']
