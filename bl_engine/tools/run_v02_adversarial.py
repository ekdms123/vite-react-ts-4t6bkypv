from __future__ import annotations
from pathlib import Path
from dataclasses import replace
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from stateful_author.executability import ADVERSARIAL_FAMILIES
from stateful_author.intelligence import load_intelligence_library
from stateful_author.runtime import (
    SceneContract, prepare_scene, verify_proposal, commit_verified, state_hash, _prepared_hash,
)
from stateful_author.contracts import StateDelta, TransformationRecord, CheckReceipt, VerificationRecord, QualificationStatus
from stateful_author.verifier import VerificationEvidence
from stateful_author.surface import evaluate_paragraph_topology
from stateful_author.model_prior import audit_model_prior
from stateful_author.creative import CandidateConcept,CandidateGenealogy,CreativeSearchMode,same_basin
from stateful_author.repair import invalidate_check_receipts

LIB=load_intelligence_library(ROOT/'author/intelligence/cards')


def _bool_error(fn, contains: str | None=None) -> bool:
    try:
        fn()
    except ValueError as exc:
        return contains is None or contains in str(exc)
    return False


def run():
    state={
        '_version':'v1',
        'narrative_state':{
            'knowledge_by_actor':{'A':['door','inactive_secret'],'B':['other_actor_secret']},
            'active_knowledge_by_actor':{'A':['door']},
            'hidden_master_plan':'MASTER_SECRET',
            'objective_affordances':['secret_exit'],
            'perceived_affordances_by_actor':{'A':['front']},
        },
        'reader_model':{'correct_answer':'CORRECT_B','hidden_reader_target':'CHOOSE_A'},
    }
    c=SceneContract('adv','A','write',parent_state_version='v1',parent_state_hash=state_hash(state))
    prepared=prepare_scene(c,state,LIB,scene_signals={})

    details={}

    # AUTHORITY_ESCAPE: lexical authority + semantic event authority must fail closed.
    hard_ban=verify_proposal(prepared,text='금지어',context={'hard_user_bans':('금지어',)}).qualification is QualificationStatus.FAIL
    req=prepare_scene(
        SceneContract('req','A','write',required_events=('door_opens',),parent_state_version='v1',parent_state_hash=state_hash(state)),
        state,LIB,scene_signals={}
    )
    required_event_missing=verify_proposal(req,text='그는 문 앞에 섰다.',context={}).qualification is QualificationStatus.ASSURANCE_NOT_MET
    ban=prepare_scene(
        SceneContract('ban','A','write',active_prohibitions=('new_character_enters',),parent_state_version='v1',parent_state_hash=state_hash(state)),
        state,LIB,scene_signals={}
    )
    prohibited_obs=VerificationEvidence(
        'auth-ban','AUTHORITY_CONTRACT',{'event_id':'new_character_enters','occurred':True},
        'MODEL_OBSERVATION',.95,('span:1',)
    )
    prohibited_event_grounded=verify_proposal(
        ban,text='누군가 문 쪽에서 움직였다.',context={},external_observations=(prohibited_obs,)
    ).qualification is QualificationStatus.FAIL
    details['AUTHORITY_ESCAPE']={
        'hard_user_ban':hard_ban,
        'required_event_missing':required_event_missing,
        'prohibited_event_grounded':prohibited_event_grounded,
    }

    # ORACLE_LEAK: hidden planner truth must neither enter packet nor survive exact-literal verification.
    blob=json.dumps(prepared.writer_packet,ensure_ascii=False)
    packet_projection=all(x not in blob for x in ('MASTER_SECRET','secret_exit','CORRECT_B','CHOOSE_A','other_actor_secret'))
    inactive_focal_knowledge='inactive_secret' not in blob and 'door' in blob
    proposal_hidden_literal=verify_proposal(prepared,text='MASTER_SECRET',context={}).qualification is QualificationStatus.FAIL
    details['ORACLE_LEAK']={
        'packet_projection':packet_projection,
        'inactive_focal_knowledge':inactive_focal_knowledge,
        'proposal_hidden_literal':proposal_hidden_literal,
    }

    # VERIFICATION_FORGERY: skipped check, prepared tamper, and forged check receipt.
    missing_required=(*prepared.required_verifier_set,'MISSING_CHECK')
    missing_prepared=replace(
        prepared,
        required_verifier_set=missing_required,
        prepared_scene_hash=_prepared_hash(prepared.contract,prepared.parent_state_hash,prepared.writer_packet,missing_required,prepared.verification_guard),
    )
    missing_check=verify_proposal(missing_prepared,text='문장.',context={}).qualification is QualificationStatus.ASSURANCE_NOT_MET

    tampered_packet=json.loads(json.dumps(prepared.writer_packet,ensure_ascii=False))
    tampered_packet['scene']['requested_action']='tampered after prepare'
    tampered=replace(prepared,writer_packet=tampered_packet)
    prepared_tamper=verify_proposal(tampered,text='문장.',context={}).qualification is QualificationStatus.ASSURANCE_NOT_MET

    record=verify_proposal(prepared,text='문장.',context={})
    bad_receipts=list(record.check_receipts)
    first=bad_receipts[0]
    bad_receipts[0]=CheckReceipt(
        first.check_id,first.check_version,'tampered',first.execution_status,first.verdict,
        first.evidence_refs,first.findings,first.deterministic,first.confidence,first.dependency_receipts
    )
    forged=VerificationRecord(
        record.scene_id,record.proposal_hash,record.prepared_scene_hash,record.parent_state_version,record.parent_state_hash,
        record.required_checks,record.executed_checks,tuple(bad_receipts),(),(),QualificationStatus.PASS,record.selected_card_ids
    )
    receipt_tamper=_bool_error(lambda: commit_verified(state,prepared,forged,StateDelta(proposal_hash=record.proposal_hash)),'STALE_OR_FORGED_CHECK_RECEIPT')
    details['VERIFICATION_FORGERY']={
        'missing_check':missing_check,
        'prepared_tamper':prepared_tamper,
        'receipt_tamper':receipt_tamper,
    }

    # STATE_MUTATION: same version with changed semantic state + proposal-swapped delta.
    stale={**state,'narrative_state':{**state['narrative_state'],'knowledge_by_actor':{'A':['changed']}}}
    stale_parent=_bool_error(lambda: commit_verified(stale,prepared,record,StateDelta(proposal_hash=record.proposal_hash)),'STALE_PARENT_STATE')
    wrong_hash='f'*64 if record.proposal_hash != 'f'*64 else 'e'*64
    wrong_delta=StateDelta(
        proposal_hash=wrong_hash,
        fact_delta=(TransformationRecord('facts','door','locked','open','different proposal','SCENE',('proposal:'+wrong_hash,)),),
    )
    proposal_mismatch=_bool_error(lambda: commit_verified(state,prepared,record,wrong_delta),'STATE_DELTA_PROPOSAL_MISMATCH')
    details['STATE_MUTATION']={'stale_parent':stale_parent,'proposal_mismatch':proposal_mismatch}

    # MODEL_PRIOR_EVASION: structural newline mutations + rhetorical paraphrase family.
    stair='하나.\n둘. 셋.\n넷.\n다섯. 여섯.\n일곱.'
    rhet='처음에는 A라 여겼다. 남은 것은 B였다. A 때문은 아니었다. 실제로 남은 건 B였다.'
    details['MODEL_PRIOR_EVASION']={
        'staircase_mutation':'PARAGRAPH_FRAGMENTATION' in evaluate_paragraph_topology(stair),
        'rhetorical_mutation':'FORMULAIC_RHETORIC' in audit_model_prior(rhet,{}),
    }

    # CREATIVE_COLLAPSE: cosmetic prose-level variation must not count as distinct conception genealogy.
    g=CandidateGenealogy(('x',),(),'GOAL',(), 'MODEL_DEFAULT',(),())
    a=CandidateConcept('A',CreativeSearchMode.EXPLORE,('x',),'one','f','k','o','r','q',genealogy=g)
    b=CandidateConcept('B',CreativeSearchMode.EXPLORE,('x',),'paraphrase','f2','k2','o2','r2','q2',genealogy=g)
    details['CREATIVE_COLLAPSE']={'same_genealogy':same_basin(a,b)}

    # REPAIR_ESCAPE: paragraph/wording edits invalidate surface receipt while retaining unaffected knowledge receipt.
    pr=CheckReceipt('PARAGRAPH_TOPOLOGY','1','h','EXECUTED','PASS',('e',))
    kr=CheckReceipt('KNOWLEDGE_REACHABILITY','1','h','EXECUTED','PASS',('e2',))
    kept=[x.check_id for x in invalidate_check_receipts((pr,kr),{'WORDING','PARAGRAPH_STRUCTURE'})]
    details['REPAIR_ESCAPE']={'receipt_invalidation':kept==['KNOWLEDGE_REACHABILITY']}

    # SELF_CONTAMINATION: generated scene output cannot grant itself durable author-style authority.
    voice=StateDelta(
        proposal_hash=record.proposal_hash,
        voice_delta=(TransformationRecord('voice','style','old','new','generated','SCENE',('proposal:'+record.proposal_hash,)),),
    )
    details['SELF_CONTAMINATION']={
        'generated_voice_commit':_bool_error(lambda: commit_verified(state,prepared,record,voice),'SELF_CONTAMINATION_FORBIDDEN')
    }

    families={family:all(details.get(family,{}).values()) for family in ADVERSARIAL_FAMILIES}
    return {
        'schema_version':'0.2',
        'families':families,
        'details':details,
        'all_pass':all(families.values()),
    }


if __name__=='__main__':
    report=run()
    out=ROOT/'verify/V02_ADVERSARIAL_RESULTS.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True))
    raise SystemExit(0 if report['all_pass'] else 1)
