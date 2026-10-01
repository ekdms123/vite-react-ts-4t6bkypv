from dataclasses import replace
import pytest

from stateful_author.intelligence import load_intelligence_library
from stateful_author.runtime import (
    SceneContract, QualificationStatus, prepare_scene, verify_proposal, commit_verified,
)
from stateful_author.contracts import StateDelta, TransformationRecord
from stateful_author.verifier import VerificationEvidence, verify_external_evidence

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]
LIB = load_intelligence_library(ROOT / 'author/intelligence/cards')
BASE = {
    '_version': 'v1',
    'narrative_state': {'knowledge_by_actor': {'A': ['door_locked']}},
    'relationship_state': {},
}


def _prepared():
    from stateful_author.runtime import state_hash
    contract = SceneContract('s1', 'A', 'write scene', parent_state_version='v1', parent_state_hash=state_hash(BASE))
    return prepare_scene(contract, BASE, LIB, scene_signals={})


def test_official_verification_computes_failures_instead_of_accepting_caller_failure_list():
    prepared = _prepared()
    with pytest.raises(TypeError):
        verify_proposal(prepared, text='문장.', failures=[])
    record = verify_proposal(prepared, text='문장.', context={})
    assert record.qualification is QualificationStatus.PASS
    assert set(record.required_checks) <= set(record.executed_checks)
    assert record.check_receipts


def test_missing_required_check_is_assurance_not_met_even_when_executed_checks_pass():
    from stateful_author.runtime import _prepared_hash
    base=_prepared()
    required=('PARAGRAPH_TOPOLOGY', 'NONEXISTENT_REQUIRED_CHECK')
    prepared = replace(base, required_verifier_set=required,
                       prepared_scene_hash=_prepared_hash(base.contract,base.parent_state_hash,base.writer_packet,required,base.verification_guard))
    record = verify_proposal(prepared, text='문장.', context={})
    assert record.qualification is QualificationStatus.ASSURANCE_NOT_MET
    assert 'NONEXISTENT_REQUIRED_CHECK' not in record.executed_checks
    assert 'MISSING_REQUIRED_CHECK:NONEXISTENT_REQUIRED_CHECK' in record.critical_unknowns


def test_external_semantic_evidence_cannot_be_verified_without_evidence_refs():
    weak = VerificationEvidence('e1', 'SEMANTIC_ECHO', True, 'MODEL_OBSERVATION', .95)
    failures = verify_external_evidence([weak])
    assert 'EXTERNAL_EVIDENCE_MISSING_REFS:e1' in failures
    grounded = VerificationEvidence('e2', 'SEMANTIC_ECHO', True, 'MODEL_OBSERVATION', .95, ('span:1',))
    assert verify_external_evidence([grounded]) == []


def test_same_version_state_mutation_is_blocked_by_semantic_hash():
    prepared = _prepared()
    record = verify_proposal(prepared, text='문장.', context={})
    stale = {**BASE, 'narrative_state': {'knowledge_by_actor': {'A': ['door_open']}}}
    delta = StateDelta(proposal_hash=record.proposal_hash, fact_delta=(TransformationRecord('facts', 'door', 'locked', 'open', 'scene effect', 'SCENE', ('e1',)),))
    with pytest.raises(ValueError, match='STALE_PARENT_STATE'):
        commit_verified(stale, prepared, record, delta)


def test_state_delta_is_closed_and_unknown_namespace_is_rejected():
    with pytest.raises(TypeError):
        StateDelta(arbitrary_top_level={'x': 1})
    prepared = _prepared()
    record = verify_proposal(prepared, text='문장.', context={})
    with pytest.raises(ValueError, match='STATE_DELTA_TYPED_REQUIRED'):
        commit_verified(BASE, prepared, record, {'arbitrary_top_level': {'x': 1}})


def test_fail_or_assurance_not_met_cannot_commit():
    prepared = replace(_prepared(), required_verifier_set=('NONEXISTENT_REQUIRED_CHECK',))
    record = verify_proposal(prepared, text='문장.', context={})
    assert record.qualification is QualificationStatus.ASSURANCE_NOT_MET
    with pytest.raises(ValueError, match='COMMIT_REQUIRES_PASS'):
        commit_verified(BASE, prepared, record, StateDelta(proposal_hash=record.proposal_hash))


def test_commit_requires_transformation_authority_and_provenance():
    prepared = _prepared()
    record = verify_proposal(prepared, text='문장.', context={})
    bad = StateDelta(proposal_hash=record.proposal_hash, fact_delta=(TransformationRecord('facts', 'door', 'locked', 'open', 'scene effect', '', ()),))
    with pytest.raises(ValueError, match='STATE_DELTA_TRANSFORMATION_INVALID'):
        commit_verified(BASE, prepared, record, bad)


def test_scene_contract_parent_hash_is_required_and_mismatch_fails_before_prepare():
    from stateful_author.runtime import state_hash
    with pytest.raises(ValueError, match='SCENE_PARENT_HASH_REQUIRED'):
        prepare_scene(SceneContract('nohash','A','write',parent_state_version='v1'), BASE, LIB, scene_signals={})
    wrong = SceneContract('wronghash','A','write',parent_state_version='v1',parent_state_hash='0'*64)
    with pytest.raises(ValueError, match='SCENE_PARENT_HASH_MISMATCH'):
        prepare_scene(wrong, BASE, LIB, scene_signals={})
    correct = SceneContract('okhash','A','write',parent_state_version='v1',parent_state_hash=state_hash(BASE))
    assert prepare_scene(correct, BASE, LIB, scene_signals={}).parent_state_hash == state_hash(BASE)


def test_commit_binds_prepared_scene_verification_and_nonempty_delta_to_same_proposal():
    from stateful_author.runtime import state_hash
    base_hash=state_hash(BASE)
    p1=prepare_scene(SceneContract('s1','A','write',parent_state_version='v1',parent_state_hash=base_hash), BASE, LIB, scene_signals={})
    p2=prepare_scene(SceneContract('s2','A','write',parent_state_version='v1',parent_state_hash=base_hash), BASE, LIB, scene_signals={})
    record=verify_proposal(p1,text='검증된 문장.',context={})
    delta=StateDelta(
        proposal_hash=record.proposal_hash,
        fact_delta=(TransformationRecord('facts','door','locked','open','verified scene effect','SCENE',('proposal:'+record.proposal_hash,)),),
    )
    with pytest.raises(ValueError, match='VERIFICATION_PREPARED_SCENE_MISMATCH'):
        commit_verified(BASE,p2,record,delta)
    wrong_delta=StateDelta(
        proposal_hash='f'*64,
        fact_delta=(TransformationRecord('facts','door','locked','open','different proposal','SCENE',('scene:s1',)),),
    )
    with pytest.raises(ValueError, match='STATE_DELTA_PROPOSAL_MISMATCH'):
        commit_verified(BASE,p1,record,wrong_delta)
    receipt,new_state=commit_verified(BASE,p1,record,delta)
    assert receipt.verified and new_state['facts']['door']=='open'


def test_commit_rejects_tampered_required_check_receipt_even_if_record_says_pass():
    from stateful_author.runtime import state_hash
    from stateful_author.contracts import CheckReceipt, VerificationRecord, QualificationStatus
    p=prepare_scene(SceneContract('s','A','write',parent_state_version='v1',parent_state_hash=state_hash(BASE)), BASE, LIB, scene_signals={})
    record=verify_proposal(p,text='문장.',context={})
    bad_receipts=list(record.check_receipts)
    first=bad_receipts[0]
    bad_receipts[0]=CheckReceipt(first.check_id,first.check_version,'tampered',first.execution_status,first.verdict,first.evidence_refs,first.findings,first.deterministic,first.confidence,first.dependency_receipts)
    forged=VerificationRecord(record.scene_id,record.proposal_hash,record.prepared_scene_hash,record.parent_state_version,record.parent_state_hash,record.required_checks,record.executed_checks,tuple(bad_receipts),(),(),QualificationStatus.PASS,record.selected_card_ids)
    with pytest.raises(ValueError, match='STALE_OR_FORGED_CHECK_RECEIPT'):
        commit_verified(BASE,p,forged,StateDelta(proposal_hash=record.proposal_hash))


def test_commit_rejects_unknown_transformation_authority_and_unbound_scene_evidence():
    from stateful_author.runtime import state_hash
    p=prepare_scene(SceneContract('auth','A','write',parent_state_version='v1',parent_state_hash=state_hash(BASE)), BASE, LIB, scene_signals={})
    record=verify_proposal(p,text='문장.',context={})
    unknown=StateDelta(
        proposal_hash=record.proposal_hash,
        fact_delta=(TransformationRecord('facts','x',None,'y','invent','HACKER',('proposal:'+record.proposal_hash,)),),
    )
    with pytest.raises(ValueError, match='STATE_DELTA_AUTHORITY_INVALID'):
        commit_verified(BASE,p,record,unknown)
    unbound=StateDelta(
        proposal_hash=record.proposal_hash,
        fact_delta=(TransformationRecord('facts','x',None,'y','scene fact','SCENE',('span:1',)),),
    )
    with pytest.raises(ValueError, match='SCENE_TRANSFORMATION_NOT_PROPOSAL_BOUND'):
        commit_verified(BASE,p,record,unbound)


def test_commit_rejects_pass_record_that_contains_failures_or_critical_unknowns():
    from stateful_author.runtime import state_hash
    from stateful_author.contracts import VerificationRecord, QualificationStatus
    p=prepare_scene(SceneContract('forge','A','write',parent_state_version='v1',parent_state_hash=state_hash(BASE)), BASE, LIB, scene_signals={})
    record=verify_proposal(p,text='문장.',context={})
    forged=VerificationRecord(record.scene_id,record.proposal_hash,record.prepared_scene_hash,record.parent_state_version,record.parent_state_hash,
                              record.required_checks,record.executed_checks,record.check_receipts,('FORGED_FAILURE',),(),QualificationStatus.PASS,record.selected_card_ids)
    with pytest.raises(ValueError, match='VERIFICATION_RECORD_INCONSISTENT'):
        commit_verified(BASE,p,forged,StateDelta(proposal_hash=record.proposal_hash))


def test_verification_fails_closed_if_prepared_scene_packet_changed_after_hashing():
    from stateful_author.runtime import state_hash
    p=prepare_scene(SceneContract('tamper','A','write',parent_state_version='v1',parent_state_hash=state_hash(BASE)), BASE, LIB, scene_signals={})
    p.writer_packet['scene']['requested_action']='tampered after prepare'
    record=verify_proposal(p,text='문장.',context={})
    assert record.qualification is QualificationStatus.ASSURANCE_NOT_MET
    assert 'PREPARED_SCENE_HASH_MISMATCH' in record.critical_unknowns


def test_required_event_without_grounded_observation_blocks_pass_and_typed_evidence_can_satisfy_it():
    from stateful_author.runtime import state_hash
    contract=SceneContract('req','A','write',required_events=('door_opens',),parent_state_version='v1',parent_state_hash=state_hash(BASE))
    prepared=prepare_scene(contract,BASE,LIB,scene_signals={})
    missing=verify_proposal(prepared,text='그는 문 앞에 섰다.',context={})
    assert missing.qualification is QualificationStatus.ASSURANCE_NOT_MET
    assert any(x.startswith('REQUIRED_EVENT_UNVERIFIED:door_opens') for x in missing.critical_unknowns)
    evidence=VerificationEvidence('auth1','AUTHORITY_CONTRACT',{'event_id':'door_opens','occurred':True},'MODEL_OBSERVATION',.95,('span:1',))
    ok=verify_proposal(prepared,text='그는 문 앞에 섰다.',context={},external_observations=(evidence,))
    assert ok.qualification is QualificationStatus.PASS


def test_prohibited_event_is_hard_failure_when_literal_or_grounded_observation_confirms_it():
    from stateful_author.runtime import state_hash
    contract=SceneContract('ban','A','write',active_prohibitions=('new_character_enters',),parent_state_version='v1',parent_state_hash=state_hash(BASE))
    prepared=prepare_scene(contract,BASE,LIB,scene_signals={})
    literal=verify_proposal(prepared,text='new_character_enters',context={})
    assert literal.qualification is QualificationStatus.FAIL
    evidence=VerificationEvidence('auth2','AUTHORITY_CONTRACT',{'event_id':'new_character_enters','occurred':True},'MODEL_OBSERVATION',.95,('span:1',))
    observed=verify_proposal(prepared,text='누군가 들어왔다.',context={},external_observations=(evidence,))
    assert observed.qualification is QualificationStatus.FAIL


def test_commit_receipt_carries_parent_resulting_and_proof_binding_hashes():
    from stateful_author.runtime import state_hash
    prepared=_prepared()
    record=verify_proposal(prepared,text='문장.',context={})
    delta=StateDelta(proposal_hash=record.proposal_hash)
    receipt,new_state=commit_verified(BASE,prepared,record,delta)
    assert receipt.parent_state_hash == prepared.parent_state_hash
    assert receipt.resulting_state_hash == state_hash(new_state)
    assert receipt.proposal_hash == record.proposal_hash
    assert receipt.prepared_scene_hash == prepared.prepared_scene_hash


def test_scene_receipt_schema_accepts_proof_binding_hash_fields():
    import json
    from jsonschema import Draft202012Validator
    schema=json.loads((ROOT/'state/SCENE_RECEIPT_SCHEMA.json').read_text())
    payload={
        'scene_id':'s1','qualification_status':'PASS','parent_state_version':'v1',
        'parent_state_hash':'a'*64,'proposal_hash':'b'*64,'prepared_scene_hash':'c'*64,
        'candidate_delta':{},'committed_delta':{},'voice_candidate_delta':{},
        'resulting_state_version':'v1+1','resulting_state_hash':'d'*64,
    }
    validator=Draft202012Validator(schema)
    errors=list(validator.iter_errors(payload))
    assert errors == []
    unbound={k:v for k,v in payload.items() if k not in {'parent_state_hash','proposal_hash','prepared_scene_hash','resulting_state_hash'}}
    assert list(validator.iter_errors(unbound))
