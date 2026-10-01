from pathlib import Path
import json, shutil

from stateful_author.executability import (
    ExecutionLedgerEntry, ImplementationStatus, Criticality, ClaimRecord, ClaimStatus,
    validate_execution_entries, contract_coverage, current_fingerprint,
    validate_verification_freshness, validate_claim_records, ADVERSARIAL_FAMILIES,
)
from stateful_author.release import build_release, validate_package

ROOT=Path(__file__).resolve().parents[1]


def test_execution_ledger_rejects_declared_executable_entry_with_missing_entrypoint():
    entry=ExecutionLedgerEntry(
        'X','1','DJAR_DERIVED',ImplementationStatus.HARD_GATE,
        'stateful_author.runtime','definitely_missing_entrypoint',(),('tests/test_v02_executability.py',),(),(),Criticality.RELEASE_BLOCKING,'structural only'
    )
    errors=validate_execution_entries(ROOT,(entry,))
    assert 'LEDGER_ENTRYPOINT_MISSING:X' in errors


def test_contract_coverage_reports_critical_and_noncritical_truth_separately():
    entries=(
        ExecutionLedgerEntry('A','1','USER',ImplementationStatus.HARD_GATE,'stateful_author.runtime','verify_proposal',(),('tests/test_v02_integrity_gate.py',),(),(),Criticality.RELEASE_BLOCKING,''),
        ExecutionLedgerEntry('B','2','EXPERIMENTAL',ImplementationStatus.EXPERIMENTAL,'','','',(),(),(),Criticality.EXPERIMENTAL,''),
    )
    cov=contract_coverage(ROOT,entries)
    assert cov.critical_total==1 and cov.critical_executable==1
    assert cov.total==2 and cov.executable==1


def test_verification_fingerprint_detects_stale_artifact_after_code_change(tmp_path):
    tree=tmp_path/'tree'; shutil.copytree(ROOT,tree)
    fp=current_fingerprint(tree)
    artifact={'fingerprint':fp}
    assert validate_verification_freshness(tree,artifact)==[]
    target=tree/'stateful_author'/'runtime.py'
    target.write_text(target.read_text()+'\n# freshness mutation\n')
    assert 'STALE_VERIFICATION_ARTIFACT:code_hash' in validate_verification_freshness(tree,artifact)


def test_claim_ledger_blocks_supported_claim_without_required_evidence_but_allows_assurance_not_met():
    supported=ClaimRecord('c1','literary superiority',('missing:evidence',),(),ClaimStatus.SUPPORTED)
    pending=ClaimRecord('c2','literary superiority',('missing:evidence',),(),ClaimStatus.ASSURANCE_NOT_MET)
    errors=validate_claim_records(ROOT,(supported,pending))
    assert 'CLAIM_OVERREACH:c1' in errors
    assert not any(e.endswith(':c2') for e in errors)


def test_required_adversarial_family_registry_covers_v02_attack_classes():
    required={'AUTHORITY_ESCAPE','ORACLE_LEAK','VERIFICATION_FORGERY','STATE_MUTATION','MODEL_PRIOR_EVASION','CREATIVE_COLLAPSE','REPAIR_ESCAPE','SELF_CONTAMINATION'}
    assert required <= set(ADVERSARIAL_FAMILIES)


def test_release_manifest_links_execution_claim_and_verification_hashes(tmp_path):
    tree=tmp_path/'tree'; shutil.copytree(ROOT,tree)
    # generate fresh v0.2 ledger artifacts for this copied tree
    from stateful_author.executability import write_default_ledgers, write_verification_bundle
    write_default_ledgers(tree)
    write_verification_bundle(tree, structural_status='STRUCTURALLY_VERIFIED')
    out=tmp_path/'release.zip'
    meta=build_release(tree,out)
    manifest=json.loads((tree/'RELEASE_MANIFEST.json').read_text())
    assert manifest['execution_ledger_sha256']
    assert manifest['claim_ledger_sha256']
    assert manifest['verification_bundle_sha256']
    assert validate_package(tree)['errors']==[]
    manifest['execution_ledger_sha256']='0'*64
    (tree/'RELEASE_MANIFEST.json').write_text(json.dumps(manifest))
    assert 'MANIFEST_EXECUTION_LEDGER_HASH_MISMATCH' in validate_package(tree)['errors']


def test_generated_scene_cannot_self_promote_into_durable_voice_state():
    from stateful_author.runtime import SceneContract, prepare_scene, verify_proposal, commit_verified, state_hash
    from stateful_author.contracts import StateDelta, TransformationRecord
    from stateful_author.intelligence import load_intelligence_library
    lib=load_intelligence_library(ROOT/'author/intelligence/cards')
    state={'_version':'v1','narrative_state':{'knowledge_by_actor':{'A':[]}}}
    prepared=prepare_scene(SceneContract('s','A','write',parent_state_version='v1',parent_state_hash=state_hash(state)),state,lib,scene_signals={})
    verification=verify_proposal(prepared,text='문장.',context={})
    delta=StateDelta(proposal_hash=verification.proposal_hash,voice_delta=(TransformationRecord('voice','style','old','new','generated scene sounded good','SCENE',('proposal:'+verification.proposal_hash,)),))
    try:
        commit_verified(state,prepared,verification,delta)
    except ValueError as exc:
        assert 'SELF_CONTAMINATION_FORBIDDEN' in str(exc)
    else:
        raise AssertionError('generated scene self-promoted into durable voice state')


def test_stable_frontier_summary_reports_distribution_without_universal_quality_score():
    from stateful_author.evaluation import stable_frontier_summary
    out=stable_frontier_summary([{'reader_pull':1.0,'formulaicity':.3},{'reader_pull':.5,'formulaicity':.6},{'reader_pull':.8,'formulaicity':.4}])
    assert 'reader_pull' in out['metrics'] and 'p10' in out['metrics']['reader_pull']
    assert 'universal_score' not in out


def test_execution_ledger_validates_runtime_caller_references_and_expected_concept_completeness():
    from stateful_author.executability import validate_ledger_completeness
    broken=ExecutionLedgerEntry(
        'X','1','DJAR_DERIVED',ImplementationStatus.HARD_GATE,
        'stateful_author.runtime','verify_proposal',(),('tests/test_v02_executability.py',),('stateful_author.runtime:definitely_missing_caller',),(),Criticality.RELEASE_BLOCKING,'x'
    )
    errors=validate_execution_entries(ROOT,(broken,))
    assert 'LEDGER_RUNTIME_CALLER_MISSING:X:stateful_author.runtime:definitely_missing_caller' in errors
    default=json.loads((ROOT/'verify/EXECUTION_LEDGER.json').read_text())['entries']
    stripped=default[:-1]
    completeness=validate_ledger_completeness(stripped)
    assert any(x.startswith('LEDGER_EXPECTED_CONCEPT_MISSING:') for x in completeness)


def test_adversarial_runner_reports_multiple_subattacks_for_root_bypass_families():
    from tools.run_v02_adversarial import run
    report=run()
    details=report['details']
    assert set(details['AUTHORITY_ESCAPE']) >= {'hard_user_ban','required_event_missing','prohibited_event_grounded'}
    assert set(details['ORACLE_LEAK']) >= {'packet_projection','inactive_focal_knowledge','proposal_hidden_literal'}
    assert set(details['VERIFICATION_FORGERY']) >= {'missing_check','prepared_tamper','receipt_tamper'}
    assert set(details['STATE_MUTATION']) >= {'stale_parent','proposal_mismatch'}
    assert all(all(items.values()) for items in details.values())
