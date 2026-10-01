from __future__ import annotations
from pathlib import Path
import hashlib, json, zipfile, os
from .intelligence import load_intelligence_library, SELECTABLE_CARD_IDS

_REQUIRED = [
    'START_HERE.md','KERNEL_CONTRACT.md','README.md',
    'author_analysis/SOURCE_REGISTRY.json','author_analysis/HOLDOUT_MANIFEST.json',
    'author/SOURCE_DIMENSION_OWNERSHIP.json','author/CANONICAL_SYNTHETIC_AUTHOR.md',
    'state/VOICE_CONTINUITY_SCHEMA.json','state/NARRATIVE_STATE_SCHEMA.json','state/SCENE_RECEIPT_SCHEMA.json',
    'runtime/WRITER_RUNTIME.md','runtime/WRITER_PACKET_SCHEMA.json','verify/VERIFICATION_GATE.json','VERIFICATION_REPORT.md',
    'docs/MASTER_ARCHITECTURE.md','author_analysis/DJAR_RECOMPILATION_MATRIX.md','verify/MASTER_SOAK_RESULTS.json','VERSION',
    'verify/EXECUTION_LEDGER.json','verify/CLAIM_LEDGER.json','verify/V02_VERIFICATION_BUNDLE.json','verify/BENCHMARK_PROTOCOL.json',
]
_RUNTIME_FORBIDDEN = ['미친 여름','첫 병','마왕','홍염의 연인','VOICE_DRIFT','MODEL_PRIOR_REVERSION','closure_target','MULTI_ALTITUDE_AUDIT','SOURCE_RESIDUE_AUDIT','SERIAL_FALSE_PROGRESS_AUDIT']
_EXCLUDE_PARTS = {'.pytest_cache','__pycache__','.git','dist'}
_EXCLUDE_SUFFIXES = {'.pyc','.pdf','.txt','.zip'}
_REQUIRED_DIRS = ['author/intelligence/cards']
_ALLOWED_TOP_LEVEL_DIRS = {'voice','author_analysis','author','state','cognition','serial','runtime','verify','stateful_author','tests','baseline','tools','docs','vendor'}


def _sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()


def _manifest_errors(root:Path)->list[str]:
    p=root/'RELEASE_MANIFEST.json'
    if not p.is_file(): return []
    try: obj=json.loads(p.read_text(encoding='utf-8'))
    except Exception: return ['INVALID_RELEASE_MANIFEST']
    errors=[]
    for rel,meta in obj.get('files',{}).items():
        fp=root/rel
        if not fp.is_file():
            errors.append(f'MANIFEST_MISSING_FILE:{rel}'); continue
        data=fp.read_bytes()
        if meta.get('sha256') != _sha256(data): errors.append(f'MANIFEST_HASH_MISMATCH:{rel}')
        if meta.get('bytes') != len(data): errors.append(f'MANIFEST_BYTES_MISMATCH:{rel}')
    linked=(('execution_ledger_sha256','verify/EXECUTION_LEDGER.json','MANIFEST_EXECUTION_LEDGER_HASH_MISMATCH'),
            ('claim_ledger_sha256','verify/CLAIM_LEDGER.json','MANIFEST_CLAIM_LEDGER_HASH_MISMATCH'),
            ('verification_bundle_sha256','verify/V02_VERIFICATION_BUNDLE.json','MANIFEST_VERIFICATION_BUNDLE_HASH_MISMATCH'))
    for field,rel,code in linked:
        fp=root/rel
        if fp.is_file() and obj.get(field)!=_sha256(fp.read_bytes()): errors.append(code)
    manifest_files=set(obj.get('files',{}))
    try: actual={rel for _,rel in _release_members(root)}
    except Exception: actual=set()
    for rel in sorted(actual-manifest_files): errors.append(f'MANIFEST_UNTRACKED_FILE:{rel}')
    for rel in sorted(manifest_files-actual):
        if (root/rel).is_file(): errors.append(f'MANIFEST_TRACKS_EXCLUDED_FILE:{rel}')
    return errors


def validate_package(root:str|Path, *, check_manifest:bool=True)->dict:
    root=Path(root).resolve(); errors=[]
    for rel in _REQUIRED:
        if not (root/rel).is_file(): errors.append(f'MISSING:{rel}')
    for rel in _REQUIRED_DIRS:
        if not (root/rel).is_dir(): errors.append(f'MISSING:{rel}')
    for path in root.rglob('*'):
        try:
            if path.is_symlink():
                resolved=path.resolve()
                try: resolved.relative_to(root)
                except ValueError: errors.append(f'OUT_OF_ROOT_SYMLINK:{path.relative_to(root).as_posix()}')
        except OSError:
            errors.append(f'BROKEN_SYMLINK:{path.relative_to(root).as_posix()}')
    cards_dir=root/'author/intelligence/cards'
    if cards_dir.is_dir():
        try:
            library=load_intelligence_library(cards_dir)
            if set(library)!=set(SELECTABLE_CARD_IDS): errors.append('INTELLIGENCE_CARD_SET_MISMATCH:'+','.join(sorted(set(library)^set(SELECTABLE_CARD_IDS))))
        except Exception as exc: errors.append(f'INVALID_INTELLIGENCE_LIBRARY:{exc.__class__.__name__}')
    for artifact in root.rglob('*.zip'):
        if any(part in _EXCLUDE_PARTS for part in artifact.relative_to(root).parts): continue
        errors.append(f'FORBIDDEN_INPUT_ARTIFACT:{artifact.relative_to(root).as_posix()}')
    runtime=root/'runtime/WRITER_RUNTIME.md'
    if runtime.is_file():
        text=runtime.read_text(encoding='utf-8')
        for token in _RUNTIME_FORBIDDEN:
            if token in text: errors.append(f'WRITER_RUNTIME_LEAK:{token}')
    for child in root.iterdir():
        if not child.is_dir() or child.name in _EXCLUDE_PARTS or child.name.startswith('.'): continue
        if child.name not in _ALLOWED_TOP_LEVEL_DIRS: errors.append(f'UNDECLARED_LAYER:{child.name}')
    ownership=root/'author/SOURCE_DIMENSION_OWNERSHIP.json'
    if ownership.is_file():
        try:
            obj=json.loads(ownership.read_text(encoding='utf-8'))
            for layer in ('HUMOR_COGNITION','STORY_ARCHITECTURE'):
                if 'paragraph_topology' not in obj[layer]['forbidden_to_modify']: errors.append(f'OWNERSHIP_BOUNDARY_MISSING:{layer}:paragraph_topology')
        except Exception as exc: errors.append(f'INVALID_OWNERSHIP_JSON:{exc.__class__.__name__}')
    version_path=root/'VERSION'
    pyproject=root/'pyproject.toml'
    if version_path.is_file() and pyproject.is_file():
        version=version_path.read_text(encoding='utf-8').strip()
        text=pyproject.read_text(encoding='utf-8')
        if f'version = "{version}"' not in text:
            errors.append('VERSION_SOURCE_MISMATCH')
    try:
        from .executability import load_execution_ledger,load_claim_ledger,validate_execution_entries,validate_ledger_completeness,validate_claim_records,contract_coverage,validate_verification_freshness
        ledger_path=root/'verify/EXECUTION_LEDGER.json'; claim_path=root/'verify/CLAIM_LEDGER.json'; bundle_path=root/'verify/V02_VERIFICATION_BUNDLE.json'
        if ledger_path.is_file():
            entries=load_execution_ledger(ledger_path); errors.extend(validate_execution_entries(root,entries)); errors.extend(validate_ledger_completeness(entries)); cov=contract_coverage(root,entries)
            if cov.critical_total and cov.critical_executable != cov.critical_total: errors.append('CRITICAL_CONTRACT_COVERAGE_INCOMPLETE')
        if claim_path.is_file(): errors.extend(validate_claim_records(root,load_claim_ledger(claim_path)))
        if bundle_path.is_file():
            bundle=json.loads(bundle_path.read_text(encoding='utf-8')); errors.extend(validate_verification_freshness(root,bundle))
    except Exception as exc:
        errors.append(f'EXECUTABILITY_VALIDATION_ERROR:{exc.__class__.__name__}')
    if check_manifest: errors.extend(_manifest_errors(root))
    return {'errors':list(dict.fromkeys(errors)),'warnings':[]}


def _release_members(root:Path):
    root=root.resolve()
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            resolved=path.resolve()
            try: resolved.relative_to(root)
            except ValueError: raise ValueError(f'OUT_OF_ROOT_SYMLINK:{path.relative_to(root).as_posix()}')
        if not path.is_file(): continue
        rel=path.relative_to(root)
        if rel.as_posix()=='RELEASE_MANIFEST.json': continue
        if any(part.startswith('.') for part in rel.parts): continue
        if any(part in _EXCLUDE_PARTS for part in rel.parts): continue
        if path.suffix.lower() in _EXCLUDE_SUFFIXES: continue
        yield path,rel.as_posix()


def build_release(root:str|Path,out:str|Path)->dict:
    root=Path(root); out=Path(out)
    validation=validate_package(root,check_manifest=False)
    if validation['errors']: raise ValueError('invalid package: '+'; '.join(validation['errors']))
    release=(root/'VERSION').read_text(encoding='utf-8').strip()
    manifest={'schema_version':'4.0','release':release,'files':{}}
    payload={}
    for path,rel in _release_members(root):
        data=path.read_bytes(); payload[rel]=data; manifest['files'][rel]={'sha256':_sha256(data),'bytes':len(data)}
    links={'execution_ledger_sha256':'verify/EXECUTION_LEDGER.json','claim_ledger_sha256':'verify/CLAIM_LEDGER.json','verification_bundle_sha256':'verify/V02_VERIFICATION_BUNDLE.json'}
    for field,rel in links.items():
        manifest[field]=_sha256(payload[rel]) if rel in payload else None
    manifest_bytes=json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True).encode('utf-8')
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for rel,data in payload.items(): z.writestr(rel,data)
        z.writestr('RELEASE_MANIFEST.json',manifest_bytes)
    (root/'RELEASE_MANIFEST.json').write_bytes(manifest_bytes)
    return {'zip_path':str(out),'file_count':len(payload)+1,'manifest_sha256':_sha256(manifest_bytes),'release':release}
