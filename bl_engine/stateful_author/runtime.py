from __future__ import annotations
from dataclasses import dataclass, fields, is_dataclass
from copy import deepcopy
from enum import Enum
from types import MappingProxyType
import hashlib, json
from .intelligence import select_intelligence_cards_ranked,pull_card_context,compile_authorized_payload
from .packet import build_writer_packet
from .receipt import make_scene_receipt
from .contracts import QualificationStatus, VerificationRecord, StateDelta
from .creative import distinguish_scene, decide_search, build_search_receipt, conception_to_packet, SearchPath
from .epistemic import build_active_cognitive_set
from .projection import collect_unreachable_literals
from .reader import ReaderModel, build_reader_view


@dataclass(frozen=True)
class SceneContract:
    scene_id:str
    focal_character_id:str
    requested_action:str
    required_events:tuple[str,...]=()
    active_prohibitions:tuple[str,...]=()
    locked_canon_refs:tuple[str,...]=()
    creative_freedom:str='NORMAL'
    parent_state_version:str='v0'
    narrator_mode:str='FOCAL'
    parent_state_hash:str=''
    def __post_init__(self):
        if not self.scene_id or not self.focal_character_id or not self.requested_action: raise ValueError('SCENE_CONTRACT_INVALID')
        if self.creative_freedom not in {'TIGHT','NORMAL','OPEN'}: raise ValueError('SCENE_FREEDOM_INVALID')
        for n in ('required_events','active_prohibitions','locked_canon_refs'):
            object.__setattr__(self,n,tuple(getattr(self,n)))


@dataclass(frozen=True)
class PreparedScene:
    contract:SceneContract
    selection:object
    writer_packet:dict
    parent_state_version:str
    parent_state_hash:str
    required_verifier_set:tuple[str,...]=('PARAGRAPH_TOPOLOGY','MODEL_PRIOR','KNOWLEDGE_REACHABILITY','HARD_USER_BANS')
    prepared_scene_hash:str=''
    scene_distinction:object=None
    search_receipt:object=None
    selected_conception:object=None
    active_cognitive_set:object=None
    reader_view:object=None
    verification_guard:tuple[str,...]=()


# Compatibility alias for old import sites. New official path returns VerificationRecord.
ProposalQualification = VerificationRecord


def _jsonable(v):
    if isinstance(v,Enum): return v.value
    if is_dataclass(v): return {f.name:_jsonable(getattr(v,f.name)) for f in fields(v)}
    if isinstance(v,(dict,MappingProxyType)): return {str(k):_jsonable(x) for k,x in sorted(v.items(),key=lambda kv:str(kv[0])) if str(k) not in {'_diagnostics','_ephemeral'}}
    if isinstance(v,(set,frozenset)): return sorted((_jsonable(x) for x in v),key=repr)
    if isinstance(v,(list,tuple)): return [_jsonable(x) for x in v]
    return v


def _semantic_state(state:dict):
    return {k:v for k,v in state.items() if k not in {'_version','_diagnostics','_ephemeral'}}


def state_hash(state:dict)->str:
    data=json.dumps(_jsonable(_semantic_state(state)),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(data).hexdigest()


def _prepared_hash(contract: SceneContract, parent_hash: str, packet: dict, required_checks=(), verification_guard=()) -> str:
    payload={
        'contract':_jsonable(contract), 'parent':parent_hash, 'packet':packet,
        'required_checks':list(required_checks), 'verification_guard':list(verification_guard),
    }
    return hashlib.sha256(json.dumps(_jsonable(payload),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def prepare_scene(contract:SceneContract,state:dict,library,*,scene_signals:dict,limit:int=8,candidate_concepts=())->PreparedScene:
    current_version=str(state.get('_version',contract.parent_state_version))
    if current_version != contract.parent_state_version:
        raise ValueError('SCENE_PARENT_VERSION_MISMATCH')
    current_hash=state_hash(state)
    if not contract.parent_state_hash:
        raise ValueError('SCENE_PARENT_HASH_REQUIRED')
    if contract.parent_state_hash != current_hash:
        raise ValueError('SCENE_PARENT_HASH_MISMATCH')
    selection=select_intelligence_cards_ranked(scene_signals,state,library,limit=limit)
    payloads=[]
    for ranked in selection.selected:
        ctx=pull_card_context(ranked.card,state)
        payloads.append(compile_authorized_payload(ranked.card,ctx,scene_signals))
    distinction=distinguish_scene(contract,scene_signals,state)
    decision=decide_search(contract,distinction)
    search_receipt=build_search_receipt(decision,candidate_concepts)
    selected=search_receipt.selected_conception
    packet=build_writer_packet(contract,state,payloads,library,conception=conception_to_packet(selected))
    active_cognitive_set=build_active_cognitive_set(contract.focal_character_id,state)
    raw_reader=state.get('reader_model')
    reader_model=raw_reader if isinstance(raw_reader,ReaderModel) else ReaderModel()
    reader_view=build_reader_view(reader_model)
    parent_hash=current_hash
    verification_guard=collect_unreachable_literals(contract.focal_character_id,state)
    required=['AUTHORITY_CONTRACT','PARAGRAPH_TOPOLOGY','MODEL_PRIOR','KNOWLEDGE_REACHABILITY','HARD_USER_BANS']
    if decision.path is SearchPath.HIGH_ASSURANCE: required.append('CREATIVE_SEARCH_COMPLETENESS')
    required=tuple(required)
    return PreparedScene(contract,selection,packet,contract.parent_state_version,parent_hash,required,
                         _prepared_hash(contract,parent_hash,packet,required,verification_guard),distinction,search_receipt,selected,active_cognitive_set,reader_view,verification_guard)


def verify_proposal(prepared:PreparedScene,*,text:str,context:dict|None=None,external_observations=())->VerificationRecord:
    from .verifier import execute_required_verifiers
    required=tuple(dict.fromkeys(prepared.required_verifier_set))
    expected=_prepared_hash(prepared.contract,prepared.parent_state_hash,prepared.writer_packet,required,prepared.verification_guard)
    if expected != prepared.prepared_scene_hash:
        proposal_hash=hashlib.sha256(text.encode('utf-8')).hexdigest()
        return VerificationRecord(
            scene_id=prepared.contract.scene_id, proposal_hash=proposal_hash, prepared_scene_hash=prepared.prepared_scene_hash,
            parent_state_version=prepared.parent_state_version, parent_state_hash=prepared.parent_state_hash,
            required_checks=required, executed_checks=(), check_receipts=(), failures=(),
            critical_unknowns=('PREPARED_SCENE_HASH_MISMATCH',), qualification=QualificationStatus.ASSURANCE_NOT_MET,
            selected_card_ids=tuple(r.card.id for r in prepared.selection.selected),
        )
    return execute_required_verifiers(prepared,text=text,context=context,external_observations=external_observations)


def qualify_proposal(*args, **kwargs):
    raise RuntimeError('LEGACY_QUALIFICATION_DISABLED_USE_VERIFY_PROPOSAL')


def _apply_transformation(new_state: dict, tr) -> None:
    namespace_map={
        'facts':'facts','evidence':'diegetic_evidence','knowledge':'knowledge_by_actor','beliefs':'beliefs_by_actor',
        'memory':'remembered_models_by_actor','self_model':'self_models_by_actor','relationship':'relationships',
        'affordance':'objective_affordances','world':'world','open_loop':'open_loops','recurrence':'recurrences',
        'reader':'reader_state','serial':'serial_state','voice':'voice_states',
    }
    target=namespace_map.get(tr.dimension,tr.dimension)
    if target.startswith('_'):
        raise ValueError('STATE_DELTA_NAMESPACE_INVALID')
    container=new_state.setdefault(target,{})
    if isinstance(container,dict):
        container[tr.key]=deepcopy(tr.after)
    else:
        # Typed transformation requested a keyed change against a nonmapping state shape.
        raise ValueError(f'STATE_DELTA_TARGET_NOT_MAPPING:{target}')


def _validate_verification_binding(prepared:PreparedScene, verification:VerificationRecord) -> None:
    if verification.failures or verification.critical_unknowns:
        raise ValueError('VERIFICATION_RECORD_INCONSISTENT')
    if verification.prepared_scene_hash != prepared.prepared_scene_hash:
        raise ValueError('VERIFICATION_PREPARED_SCENE_MISMATCH')
    if verification.scene_id != prepared.contract.scene_id:
        raise ValueError('VERIFICATION_PREPARED_SCENE_MISMATCH')
    if verification.parent_state_version != prepared.parent_state_version or verification.parent_state_hash != prepared.parent_state_hash:
        raise ValueError('VERIFICATION_PARENT_STATE_MISMATCH')
    required=tuple(dict.fromkeys(prepared.required_verifier_set))
    if tuple(verification.required_checks) != required or not set(required) <= set(verification.executed_checks):
        raise ValueError('VERIFICATION_REQUIRED_SET_MISMATCH')
    expected_prepared=_prepared_hash(prepared.contract,prepared.parent_state_hash,prepared.writer_packet,required,prepared.verification_guard)
    if expected_prepared != prepared.prepared_scene_hash:
        raise ValueError('PREPARED_SCENE_HASH_MISMATCH')
    from .verifier import check_input_hash, verifier_version
    receipts={r.check_id:r for r in verification.check_receipts}
    if set(receipts) != set(required):
        raise ValueError('STALE_OR_FORGED_CHECK_RECEIPT')
    for check_id in required:
        receipt=receipts[check_id]
        if receipt.execution_status != 'EXECUTED' or receipt.verdict != 'PASS':
            raise ValueError('STALE_OR_FORGED_CHECK_RECEIPT')
        if receipt.check_version != verifier_version(check_id):
            raise ValueError('STALE_OR_FORGED_CHECK_RECEIPT')
        expected_input=check_input_hash(check_id,verification.proposal_hash,prepared.prepared_scene_hash)
        if receipt.input_hash != expected_input:
            raise ValueError('STALE_OR_FORGED_CHECK_RECEIPT')


def commit_verified(state:dict,prepared:PreparedScene,verification:VerificationRecord,candidate_delta:StateDelta):
    if not isinstance(prepared,PreparedScene):
        raise ValueError('PREPARED_SCENE_REQUIRED')
    if not isinstance(verification,VerificationRecord) or verification.qualification is not QualificationStatus.PASS:
        raise ValueError('COMMIT_REQUIRES_PASS')
    if not isinstance(candidate_delta,StateDelta):
        raise ValueError('STATE_DELTA_TYPED_REQUIRED')
    _validate_verification_binding(prepared,verification)
    current_version=str(state.get('_version',prepared.parent_state_version))
    if current_version != prepared.parent_state_version or state_hash(state) != prepared.parent_state_hash:
        raise ValueError('STALE_PARENT_STATE')
    candidate_delta.validate()
    if candidate_delta.proposal_hash and candidate_delta.proposal_hash != verification.proposal_hash:
        raise ValueError('STATE_DELTA_PROPOSAL_MISMATCH')
    if candidate_delta.transformations() and candidate_delta.proposal_hash != verification.proposal_hash:
        raise ValueError('STATE_DELTA_PROPOSAL_MISMATCH')
    proposal_ref=f'proposal:{verification.proposal_hash}'
    for tr in candidate_delta.transformations():
        if tr.authority == 'SCENE' and proposal_ref not in set(tr.evidence_refs) | set(tr.provenance_refs):
            raise ValueError('SCENE_TRANSFORMATION_NOT_PROPOSAL_BOUND')
    allowed_voice_authority={'USER','SOURCE','APPROVED_STYLE','COMPILER_VALIDATED'}
    for tr in candidate_delta.voice_delta:
        if tr.authority not in allowed_voice_authority:
            raise ValueError('SELF_CONTAMINATION_FORBIDDEN')
    new_state=deepcopy(state)
    field_to_dim={
        'fact_delta':'facts','evidence_delta':'evidence','knowledge_delta':'knowledge','belief_delta':'beliefs',
        'memory_delta':'memory','self_model_delta':'self_model','relationship_delta':'relationship',
        'affordance_delta':'affordance','world_delta':'world','open_loop_delta':'open_loop',
        'recurrence_delta':'recurrence','reader_delta':'reader','serial_delta':'serial','voice_delta':'voice',
    }
    for field,default_dim in field_to_dim.items():
        for tr in getattr(candidate_delta,field):
            if tr.dimension not in {default_dim, {'fact_delta':'facts','belief_delta':'beliefs'}.get(field,default_dim)}:
                allowed_aliases={
                    'knowledge_delta':{'knowledge','knowledge_by_actor'}, 'relationship_delta':{'relationship','relationships'},
                    'affordance_delta':{'affordance','objective_affordances','perceived_affordances_by_actor'},
                    'memory_delta':{'memory','remembered_models_by_actor'}, 'self_model_delta':{'self_model','self_models_by_actor'},
                    'reader_delta':{'reader','reader_state'}, 'serial_delta':{'serial','serial_state'}, 'voice_delta':{'voice','voice_states'},
                    'recurrence_delta':{'recurrence','recurrences'}, 'open_loop_delta':{'open_loop','open_loops'},
                    'world_delta':{'world'}, 'evidence_delta':{'evidence','diegetic_evidence'}, 'fact_delta':{'facts'}, 'belief_delta':{'beliefs','beliefs_by_actor'},
                }
                if tr.dimension not in allowed_aliases[field]:
                    raise ValueError('STATE_DELTA_NAMESPACE_INVALID')
            _apply_transformation(new_state,tr)
    new_version=f'{prepared.parent_state_version}+1'
    new_state['_version']=new_version
    receipt=make_scene_receipt(
        scene_id=verification.scene_id,verified=True,state_delta={'proposal_hash':candidate_delta.proposal_hash,'transformations':[tr.__dict__ for tr in candidate_delta.transformations()]},
        proposed_voice_delta={},intelligence_cards_used=verification.selected_card_ids,parent_state_version=prepared.parent_state_version,
        verification_evidence_ids=verification.evidence_ids,resulting_state_version=new_version,
        parent_state_hash=prepared.parent_state_hash,resulting_state_hash=state_hash(new_state),
        proposal_hash=verification.proposal_hash,prepared_scene_hash=prepared.prepared_scene_hash,
    )
    return receipt,new_state
