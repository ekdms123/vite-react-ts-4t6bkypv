from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import ast, hashlib, json


class ImplementationStatus(str, Enum):
    HARD_GATE='HARD_GATE'
    RUNTIME_PRIMITIVE='RUNTIME_PRIMITIVE'
    SPECIALIST_EXECUTABLE='SPECIALIST_EXECUTABLE'
    VERIFIER_EXECUTABLE='VERIFIER_EXECUTABLE'
    EVALUATION_ONLY='EVALUATION_ONLY'
    EXPERIMENTAL='EXPERIMENTAL'
    DOCUMENTATION_ONLY='DOCUMENTATION_ONLY'


class Criticality(str, Enum):
    RELEASE_BLOCKING='RELEASE_BLOCKING'
    REQUIRED='REQUIRED'
    OPTIONAL='OPTIONAL'
    EXPERIMENTAL='EXPERIMENTAL'


class ClaimStatus(str, Enum):
    SUPPORTED='SUPPORTED'
    PARTIALLY_SUPPORTED='PARTIALLY_SUPPORTED'
    ASSURANCE_NOT_MET='ASSURANCE_NOT_MET'
    REJECTED='REJECTED'


_EXECUTABLE_STATUSES={
    ImplementationStatus.HARD_GATE,ImplementationStatus.RUNTIME_PRIMITIVE,
    ImplementationStatus.SPECIALIST_EXECUTABLE,ImplementationStatus.VERIFIER_EXECUTABLE,
    ImplementationStatus.EVALUATION_ONLY,
}

ADVERSARIAL_FAMILIES=(
    'AUTHORITY_ESCAPE','ORACLE_LEAK','VERIFICATION_FORGERY','STATE_MUTATION',
    'MODEL_PRIOR_EVASION','CREATIVE_COLLAPSE','REPAIR_ESCAPE','SELF_CONTAMINATION',
)

EXPECTED_CONCEPT_IDS=frozenset({
    'MANDATORY_VERIFICATION','PASS_SET_LOGIC','NO_ORACLE_PROJECTION','NARRATOR_FOCAL_PRESERVATION',
    'SEMANTIC_STATE_HASH','TYPED_STATE_DELTA','TRANSACTIONAL_COMMIT','PARAGRAPH_TOPOLOGY',
    'REPAIR_INVALIDATION','SELF_CONTAMINATION_FIREWALL','EXECUTION_LEDGER','CONTRACT_COVERAGE',
    'VERIFICATION_FRESHNESS','CLAIM_LEDGER','MODEL_PRIOR_FIREWALL','CREATIVE_SEARCH_CONTROLLER',
    'PARTIAL_COGNITIVE_WORLD','READER_VIEW','EMERGENT_INTERACTION','STABLE_FRONTIER_SUMMARY',
    'SOCIAL_ROLE_PRIOR_AUDIT','BLIND_LITERARY_SUPERIORITY',
})



def _tuple(value):
    if value in (None,''): return ()
    if isinstance(value,tuple): return value
    if isinstance(value,(list,set,frozenset)): return tuple(value)
    return (value,)


@dataclass(frozen=True)
class ExecutionLedgerEntry:
    concept_id: str
    spec_section: str
    epistemic_class: str
    implementation_status: ImplementationStatus
    module: str=''
    entrypoint: str=''
    schema_refs: tuple[str,...]=()
    test_refs: tuple[str,...]=()
    runtime_callers: tuple[str,...]=()
    downstream_consumers: tuple[str,...]=()
    criticality: Criticality=Criticality.OPTIONAL
    claim_boundary: str=''
    def __post_init__(self):
        if not isinstance(self.implementation_status,ImplementationStatus):
            object.__setattr__(self,'implementation_status',ImplementationStatus(self.implementation_status))
        if not isinstance(self.criticality,Criticality):
            object.__setattr__(self,'criticality',Criticality(self.criticality))
        for name in ('schema_refs','test_refs','runtime_callers','downstream_consumers'):
            object.__setattr__(self,name,_tuple(getattr(self,name)))


@dataclass(frozen=True)
class ClaimRecord:
    claim_id: str
    claim_text: str
    required_evidence: tuple[str,...]=()
    current_evidence_refs: tuple[str,...]=()
    status: ClaimStatus=ClaimStatus.ASSURANCE_NOT_MET
    expiration_condition: str=''
    def __post_init__(self):
        object.__setattr__(self,'required_evidence',_tuple(self.required_evidence))
        object.__setattr__(self,'current_evidence_refs',_tuple(self.current_evidence_refs))
        if not isinstance(self.status,ClaimStatus): object.__setattr__(self,'status',ClaimStatus(self.status))


@dataclass(frozen=True)
class ContractCoverage:
    total: int
    executable: int
    critical_total: int
    critical_executable: int
    required_total: int
    required_executable: int
    experimental: int
    documentation_only: int
    errors: tuple[str,...]=()
    def to_dict(self):
        return {
            'total':self.total,'executable':self.executable,
            'coverage':round(self.executable/max(1,self.total),4),
            'critical_total':self.critical_total,'critical_executable':self.critical_executable,
            'critical_coverage':round(self.critical_executable/max(1,self.critical_total),4),
            'required_total':self.required_total,'required_executable':self.required_executable,
            'required_coverage':round(self.required_executable/max(1,self.required_total),4),
            'experimental':self.experimental,'documentation_only':self.documentation_only,'errors':list(self.errors),
        }


def _module_file(root:Path,module:str)->Path:
    return root.joinpath(*module.split('.')).with_suffix('.py')


def _top_level_names(path:Path)->set[str]:
    try: tree=ast.parse(path.read_text(encoding='utf-8'))
    except Exception: return set()
    return {node.name for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}


def validate_execution_entries(root:str|Path, entries) -> list[str]:
    root=Path(root); errors=[]
    for entry in entries:
        if not isinstance(entry,ExecutionLedgerEntry):
            errors.append('LEDGER_ENTRY_UNTYPED'); continue
        if entry.implementation_status in _EXECUTABLE_STATUSES:
            if not entry.module:
                errors.append(f'LEDGER_MODULE_MISSING:{entry.concept_id}')
            else:
                path=_module_file(root,entry.module)
                if not path.is_file(): errors.append(f'LEDGER_MODULE_FILE_MISSING:{entry.concept_id}')
                elif entry.entrypoint and entry.entrypoint not in _top_level_names(path):
                    errors.append(f'LEDGER_ENTRYPOINT_MISSING:{entry.concept_id}')
            if not entry.test_refs:
                errors.append(f'LEDGER_TEST_REF_MISSING:{entry.concept_id}')
        for ref in entry.test_refs:
            if not (root/ref).is_file(): errors.append(f'LEDGER_TEST_FILE_MISSING:{entry.concept_id}:{ref}')
        for ref in entry.schema_refs:
            if not (root/ref).is_file(): errors.append(f'LEDGER_SCHEMA_FILE_MISSING:{entry.concept_id}:{ref}')
        for ref in (*entry.runtime_callers,*entry.downstream_consumers):
            if ':' not in ref:
                errors.append(f'LEDGER_RUNTIME_REF_INVALID:{entry.concept_id}:{ref}'); continue
            module,name=ref.split(':',1); path=_module_file(root,module)
            if not path.is_file() or name not in _top_level_names(path):
                errors.append(f'LEDGER_RUNTIME_CALLER_MISSING:{entry.concept_id}:{ref}')
    return list(dict.fromkeys(errors))


def validate_ledger_completeness(entries) -> list[str]:
    ids=[]
    for entry in entries:
        if isinstance(entry,ExecutionLedgerEntry): ids.append(entry.concept_id)
        elif isinstance(entry,dict): ids.append(str(entry.get('concept_id','')))
        else: ids.append('')
    errors=[]
    seen=set()
    for concept_id in ids:
        if not concept_id: errors.append('LEDGER_CONCEPT_ID_MISSING'); continue
        if concept_id in seen: errors.append(f'LEDGER_CONCEPT_DUPLICATE:{concept_id}')
        seen.add(concept_id)
    for concept_id in sorted(EXPECTED_CONCEPT_IDS-seen):
        errors.append(f'LEDGER_EXPECTED_CONCEPT_MISSING:{concept_id}')
    for concept_id in sorted(seen-EXPECTED_CONCEPT_IDS):
        errors.append(f'LEDGER_UNDECLARED_CONCEPT:{concept_id}')
    return list(dict.fromkeys(errors))


def contract_coverage(root:str|Path, entries) -> ContractCoverage:
    root=Path(root); entries=tuple(entries); executable=0; critical_total=critical_executable=0; required_total=required_executable=0
    all_errors=[]
    for entry in entries:
        errs=validate_execution_entries(root,(entry,)); all_errors.extend(errs)
        ok=entry.implementation_status in _EXECUTABLE_STATUSES and not errs
        executable += int(ok)
        if entry.criticality is Criticality.RELEASE_BLOCKING:
            critical_total+=1; critical_executable+=int(ok)
        if entry.criticality is Criticality.REQUIRED:
            required_total+=1; required_executable+=int(ok)
    return ContractCoverage(len(entries),executable,critical_total,critical_executable,required_total,required_executable,
                            sum(e.implementation_status is ImplementationStatus.EXPERIMENTAL for e in entries),
                            sum(e.implementation_status is ImplementationStatus.DOCUMENTATION_ONLY for e in entries),
                            tuple(dict.fromkeys(all_errors)))


def validate_claim_records(root:str|Path, records) -> list[str]:
    errors=[]
    for record in records:
        if not isinstance(record,ClaimRecord): errors.append('CLAIM_ENTRY_UNTYPED'); continue
        if record.status is ClaimStatus.SUPPORTED and not set(record.required_evidence) <= set(record.current_evidence_refs):
            errors.append(f'CLAIM_OVERREACH:{record.claim_id}')
    return errors


def _hash_paths(root:Path, paths:list[Path])->str:
    h=hashlib.sha256()
    for path in sorted(paths,key=lambda p:p.as_posix()):
        if not path.is_file(): continue
        rel=path.relative_to(root).as_posix().encode(); data=path.read_bytes()
        h.update(len(rel).to_bytes(4,'big')); h.update(rel); h.update(len(data).to_bytes(8,'big')); h.update(data)
    return h.hexdigest()


def _file_hash(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else hashlib.sha256(b'').hexdigest()


def current_fingerprint(root:str|Path)->dict:
    root=Path(root)
    code=[]
    for base in ('stateful_author','tools'):
        d=root/base
        if d.is_dir(): code.extend(p for p in d.rglob('*.py') if '__pycache__' not in p.parts)
    schemas=[]
    for base in ('runtime','state','serial','verify'):
        d=root/base
        if d.is_dir(): schemas.extend(p for p in d.rglob('*.json') if p.name not in {'EXECUTION_LEDGER.json','CLAIM_LEDGER.json','V02_VERIFICATION_BUNDLE.json','V02_ADVERSARIAL_RESULTS.json','MASTER_SOAK_RESULTS.json'})
    return {
        'code_hash':_hash_paths(root,code),
        'schema_hash':_hash_paths(root,schemas),
        'execution_ledger_hash':_file_hash(root/'verify/EXECUTION_LEDGER.json'),
        'claim_ledger_hash':_file_hash(root/'verify/CLAIM_LEDGER.json'),
        'version_hash':_file_hash(root/'VERSION'),
    }


def validate_verification_freshness(root:str|Path, artifact:dict)->list[str]:
    current=current_fingerprint(root); stored=artifact.get('fingerprint',{}) if isinstance(artifact,dict) else {}
    errors=[]
    for key,value in current.items():
        if stored.get(key)!=value: errors.append(f'STALE_VERIFICATION_ARTIFACT:{key}')
    return errors


def _entry(*args,**kwargs): return ExecutionLedgerEntry(*args,**kwargs)


def default_execution_entries() -> tuple[ExecutionLedgerEntry,...]:
    RB=Criticality.RELEASE_BLOCKING; R=Criticality.REQUIRED; O=Criticality.OPTIONAL; X=Criticality.EXPERIMENTAL
    return (
        _entry('MANDATORY_VERIFICATION','45-47','DJAR_DERIVED',ImplementationStatus.HARD_GATE,'stateful_author.runtime','verify_proposal',(),('tests/test_v02_integrity_gate.py',),('stateful_author.verifier:execute_required_verifiers',),(),RB,'PASS requires executed required checks.'),
        _entry('PASS_SET_LOGIC','47','DJAR_DERIVED',ImplementationStatus.VERIFIER_EXECUTABLE,'stateful_author.verifier','execute_required_verifiers',(),('tests/test_v02_integrity_gate.py',),(),(),RB,'Missing required checks produce ASSURANCE_NOT_MET.'),
        _entry('NO_ORACLE_PROJECTION','28-29','USER_AUTHORITATIVE',ImplementationStatus.HARD_GATE,'stateful_author.projection','build_realization_packet',('runtime/WRITER_PACKET_SCHEMA.json',),('tests/test_v02_projection.py',),('stateful_author.packet:build_writer_packet',),(),RB,'Writer receives positive-constructed partial state only.'),
        _entry('NARRATOR_FOCAL_PRESERVATION','29','USER_AUTHORITATIVE',ImplementationStatus.HARD_GATE,'stateful_author.packet','build_writer_packet',('runtime/WRITER_PACKET_SCHEMA.json',),('tests/test_v02_projection.py',),(),(),RB,'Focal id and narrator mode survive exactly.'),
        _entry('SEMANTIC_STATE_HASH','53-54','DJAR_DERIVED',ImplementationStatus.HARD_GATE,'stateful_author.runtime','state_hash',(),('tests/test_v02_integrity_gate.py',),(),(),RB,'Semantic hash excludes ephemeral/version metadata but detects durable mutation.'),
        _entry('TYPED_STATE_DELTA','52','DJAR_DERIVED',ImplementationStatus.RUNTIME_PRIMITIVE,'stateful_author.contracts','StateDelta',(),('tests/test_v02_integrity_gate.py',),(),(),RB,'Closed namespaces only.'),
        _entry('TRANSACTIONAL_COMMIT','53','DJAR_DERIVED',ImplementationStatus.HARD_GATE,'stateful_author.runtime','commit_verified',(),('tests/test_v02_integrity_gate.py','tests/test_v02_executability.py'),(),(),RB,'PASS + version + semantic hash + authority/provenance required.'),
        _entry('PARAGRAPH_TOPOLOGY','34','USER_AUTHORITATIVE',ImplementationStatus.VERIFIER_EXECUTABLE,'stateful_author.surface','evaluate_paragraph_topology',(),('tests/test_v02_model_prior.py',),(),(),RB,'Mutation-family topology checks; no fixed length recipe.'),
        _entry('REPAIR_INVALIDATION','51','DJAR_DERIVED',ImplementationStatus.HARD_GATE,'stateful_author.repair','invalidate_check_receipts',(),('tests/test_v02_model_prior.py',),(),(),RB,'Affected receipts are invalidated after repair.'),
        _entry('SELF_CONTAMINATION_FIREWALL','55','USER_AUTHORITATIVE',ImplementationStatus.HARD_GATE,'stateful_author.runtime','commit_verified',(),('tests/test_v02_executability.py',),(),(),RB,'Generated scene authority cannot update durable voice identity.'),
        _entry('EXECUTION_LEDGER','56-58','DJAR_DERIVED',ImplementationStatus.HARD_GATE,'stateful_author.executability','validate_execution_entries',(),('tests/test_v02_executability.py',),(),(),RB,'Executable claims map to reachable code/schema/tests.'),
        _entry('CONTRACT_COVERAGE','58','DJAR_DERIVED',ImplementationStatus.HARD_GATE,'stateful_author.executability','contract_coverage',(),('tests/test_v02_executability.py',),(),(),RB,'Critical and noncritical coverage reported separately.'),
        _entry('VERIFICATION_FRESHNESS','60','DJAR_DERIVED',ImplementationStatus.HARD_GATE,'stateful_author.executability','validate_verification_freshness',(),('tests/test_v02_executability.py',),(),(),RB,'Verification evidence binds code/schema/ledger/version hashes.'),
        _entry('CLAIM_LEDGER','59','DJAR_DERIVED',ImplementationStatus.HARD_GATE,'stateful_author.executability','validate_claim_records',(),('tests/test_v02_executability.py',),(),(),RB,'Supported claims require declared evidence.'),
        _entry('MODEL_PRIOR_FIREWALL','35-44','USER_AUTHORITATIVE',ImplementationStatus.VERIFIER_EXECUTABLE,'stateful_author.model_prior','audit_model_prior_detailed',(),('tests/test_v02_model_prior.py',),(),(),R,'Scoped lexical/rhetorical/affective/discourse heuristics; suspicion is not universal ban.'),
        _entry('CREATIVE_SEARCH_CONTROLLER','14-20','DJAR_DERIVED',ImplementationStatus.SPECIALIST_EXECUTABLE,'stateful_author.creative','decide_search',(),('tests/test_v02_creative_search.py',),(),(),R,'Search depth and structural genealogy are executable; candidate ideation still requires an external model adapter.'),
        _entry('PARTIAL_COGNITIVE_WORLD','8-10','RESEARCH_SUPPORTED',ImplementationStatus.RUNTIME_PRIMITIVE,'stateful_author.epistemic','build_active_cognitive_set',(),('tests/test_v02_partial_worlds.py',),(),(),R,'Stored and active knowledge remain distinct.'),
        _entry('READER_VIEW','26','RESEARCH_SUPPORTED',ImplementationStatus.RUNTIME_PRIMITIVE,'stateful_author.reader','build_reader_view',(),('tests/test_v02_partial_worlds.py',),(),(),R,'Reader activation/retrieval/tractability primitives.'),
        _entry('EMERGENT_INTERACTION','24-25','RESEARCH_SUPPORTED',ImplementationStatus.SPECIALIST_EXECUTABLE,'stateful_author.interaction','confirm_interaction_frame',(),('tests/test_v02_partial_worlds.py',),(),(),R,'Frame change confirms only after grounded generated uptake.'),
        _entry('STABLE_FRONTIER_SUMMARY','66','DJAR_DERIVED',ImplementationStatus.EVALUATION_ONLY,'stateful_author.evaluation','stable_frontier_summary',(),('tests/test_v02_executability.py',),(),(),O,'Distribution reporting only; no universal literary score.'),
        _entry('SOCIAL_ROLE_PRIOR_AUDIT','49','RESEARCH_SUPPORTED',ImplementationStatus.EXPERIMENTAL,'','',(),(),(),(),X,'Not claimed implemented in this release.'),
        _entry('BLIND_LITERARY_SUPERIORITY','65-68','EXPERIMENTAL',ImplementationStatus.EXPERIMENTAL,'','',(),(),(),(),X,'Requires controlled live generation and blind human evaluation.'),
    )


def default_claim_records() -> tuple[ClaimRecord,...]:
    return (
        ClaimRecord('STRUCTURAL_GATES','Release-blocking integrity gates are executable and regression-tested',
                    ('verify/EXECUTION_LEDGER.json','tests/test_v02_integrity_gate.py','tests/test_v02_projection.py'),
                    ('verify/EXECUTION_LEDGER.json','tests/test_v02_integrity_gate.py','tests/test_v02_projection.py'),ClaimStatus.SUPPORTED),
        ClaimRecord('MODEL_PRIOR_MUTATION_COVERAGE','Paragraph/model-prior regression suite covers multiple surface mutation families',
                    ('tests/test_v02_model_prior.py',),('tests/test_v02_model_prior.py',),ClaimStatus.SUPPORTED),
        ClaimRecord('LITERARY_SUPERIORITY','v0.2 is blindly preferred or universally more literary',
                    ('external:controlled-generation','external:blind-human-evaluation'),(),ClaimStatus.ASSURANCE_NOT_MET),
        ClaimRecord('COMMERCIAL_LIFT','v0.2 improves sales or retention',('external:commercial-outcome-study',),(),ClaimStatus.ASSURANCE_NOT_MET),
        ClaimRecord('MAD_SUMMER_EXACT_STYLOMETRY','Exact Korean prose manifold from image-only source PDFs',('source:text-extraction-or-grounded-corpus',),(),ClaimStatus.ASSURANCE_NOT_MET),
    )


def _entry_to_json(e:ExecutionLedgerEntry)->dict:
    d=asdict(e); d['implementation_status']=e.implementation_status.value; d['criticality']=e.criticality.value
    return d


def _claim_to_json(c:ClaimRecord)->dict:
    d=asdict(c); d['status']=c.status.value; return d


def write_default_ledgers(root:str|Path) -> dict:
    root=Path(root); (root/'verify').mkdir(parents=True,exist_ok=True)
    entries=default_execution_entries(); claims=default_claim_records()
    ledger={'schema_version':'0.2','entries':[_entry_to_json(e) for e in entries]}
    claim={'schema_version':'0.2','claims':[_claim_to_json(c) for c in claims]}
    (root/'verify/EXECUTION_LEDGER.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (root/'verify/CLAIM_LEDGER.json').write_text(json.dumps(claim,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return {'execution_entries':entries,'claim_records':claims}


def load_execution_ledger(path:str|Path)->tuple[ExecutionLedgerEntry,...]:
    obj=json.loads(Path(path).read_text(encoding='utf-8'))
    return tuple(ExecutionLedgerEntry(**item) for item in obj.get('entries',()))


def load_claim_ledger(path:str|Path)->tuple[ClaimRecord,...]:
    obj=json.loads(Path(path).read_text(encoding='utf-8'))
    return tuple(ClaimRecord(**item) for item in obj.get('claims',()))


def write_verification_bundle(root:str|Path, *, structural_status:str='STRUCTURAL_CANDIDATE', test_summary:dict|None=None, adversarial_summary:dict|None=None)->dict:
    root=Path(root)
    if not (root/'verify/EXECUTION_LEDGER.json').is_file() or not (root/'verify/CLAIM_LEDGER.json').is_file():
        write_default_ledgers(root)
    entries=load_execution_ledger(root/'verify/EXECUTION_LEDGER.json'); claims=load_claim_ledger(root/'verify/CLAIM_LEDGER.json')
    ledger_errors=validate_execution_entries(root,entries)+validate_ledger_completeness(entries); claim_errors=validate_claim_records(root,claims); coverage=contract_coverage(root,entries)
    if structural_status=='STRUCTURALLY_VERIFIED' and (ledger_errors or claim_errors or coverage.critical_executable!=coverage.critical_total):
        raise ValueError('STRUCTURAL_VERIFICATION_PRECONDITIONS_NOT_MET')
    bundle={
        'schema_version':'0.2','structural_status':structural_status,'fingerprint':current_fingerprint(root),
        'contract_coverage':coverage.to_dict(),'ledger_errors':ledger_errors,'claim_errors':claim_errors,
        'adversarial_families':list(ADVERSARIAL_FAMILIES),'test_summary':test_summary or {},'adversarial_summary':adversarial_summary or {},
        'literary_validation':'ASSURANCE_NOT_MET',
    }
    (root/'verify/V02_VERIFICATION_BUNDLE.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return bundle
