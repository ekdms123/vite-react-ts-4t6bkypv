from __future__ import annotations
from dataclasses import dataclass
import hashlib
from .surface import evaluate_paragraph_topology
from .voice import portable_line_risk
from .model_prior import audit_model_prior
from .intelligence import SceneSignal, SignalSource
from .contracts import CheckReceipt, VerificationRecord, QualificationStatus


@dataclass(frozen=True)
class VerificationEvidence:
    evidence_id: str
    check_id: str
    value: object
    source: str
    confidence: float
    evidence_refs: tuple[str, ...] = ()
    def __post_init__(self):
        if not 0 <= float(self.confidence) <= 1:
            raise ValueError('VERIFICATION_CONFIDENCE_OUT_OF_RANGE')
        object.__setattr__(self,'evidence_refs',tuple(self.evidence_refs))


def verify_external_evidence(items) -> list[str]:
    failures=[]
    for item in items:
        if not isinstance(item,VerificationEvidence):
            failures.append('EXTERNAL_EVIDENCE_UNTYPED')
            continue
        threshold=0.5 if item.source in {'USER','STATE','DIRECT_DETERMINISTIC','STATE_DERIVED'} else 0.8
        if item.confidence < threshold:
            failures.append(f'EXTERNAL_EVIDENCE_INSUFFICIENT:{item.evidence_id}')
        if item.source not in {'USER','STATE','DIRECT_DETERMINISTIC','STATE_DERIVED'} and not item.evidence_refs:
            failures.append(f'EXTERNAL_EVIDENCE_MISSING_REFS:{item.evidence_id}')
    return list(dict.fromkeys(failures))

@dataclass(frozen=True)
class VerificationResult:
    failures:list[str]


def verify_scene(text:str,context:dict)->VerificationResult:
    failures=[]
    failures.extend(evaluate_paragraph_topology(text))
    failures.extend(audit_model_prior(text,context))
    generic_signals=0
    if context.get('generic_emotional_line') or portable_line_risk(text,set(context.get('context_tokens',set()))): generic_signals+=1
    if context.get('abstract_story_metaphor'): generic_signals+=1
    if context.get('reality_anchor_count',1)==0: generic_signals+=1
    if generic_signals>=3: failures.append('MODEL_PRIOR_REVERSION')
    if context.get('mode')=='MEMORY' and context.get('chronology_summary_ratio',0)>=0.7 and not context.get('present_relevance',True): failures.append('NARRATIVE_MODE_DRIFT')
    if context.get('terminal_beats',0)>=2 and not context.get('post_terminal_state_delta',True): failures.append('CLOSURE_STACKING')
    if context.get('meaning_recovery_count',0)>=3: failures.append('REDUNDANT_MEANING_RECOVERY')
    if context.get('unreachable_claims',0)>0: failures.append('KNOWLEDGE_LEAK')
    restricted=set(context.get('restricted_source_tokens',set()))
    if any(token and token in text for token in restricted): failures.append('SOURCE_RESIDUE')
    return VerificationResult(list(dict.fromkeys(failures)))


def check_input_hash(check_id: str, proposal_hash: str, prepared_hash: str) -> str:
    return hashlib.sha256((check_id+'|'+prepared_hash+'|'+proposal_hash).encode('utf-8')).hexdigest()


def verifier_version(check_id: str) -> str:
    return VERIFIER_VERSIONS.get(check_id,'1.0')


def _receipt(check_id: str, proposal_hash: str, prepared_hash: str, findings=(), *, deterministic=True) -> CheckReceipt:
    findings=tuple(dict.fromkeys(findings))
    input_hash=check_input_hash(check_id,proposal_hash,prepared_hash)
    evidence=(f'deterministic:{check_id}:{input_hash[:16]}',) if deterministic else ()
    return CheckReceipt(
        check_id=check_id, check_version=verifier_version(check_id), input_hash=input_hash,
        execution_status='EXECUTED', verdict='FAIL' if findings else 'PASS',
        evidence_refs=evidence, findings=findings, deterministic=deterministic,
        confidence=1.0 if deterministic else 0.8,
    )


def _valid_external_for_check(context: dict, check_id: str):
    out=[]
    for item in context.get('_external_observations',()):
        if not isinstance(item,VerificationEvidence) or item.check_id != check_id:
            continue
        if verify_external_evidence((item,)):
            continue
        out.append(item)
    return tuple(out)


def _authority_check(prepared, text, context):
    findings=[]
    evidence=_valid_external_for_check(context,'AUTHORITY_CONTRACT')
    by_event={}
    for item in evidence:
        if isinstance(item.value,dict) and isinstance(item.value.get('event_id'),str) and isinstance(item.value.get('occurred'),bool):
            by_event[item.value['event_id']]=item.value['occurred']
    for event in prepared.contract.required_events:
        if event and event in text:
            continue
        if event not in by_event:
            findings.append(f'ASSURANCE:REQUIRED_EVENT_UNVERIFIED:{event}')
        elif not by_event[event]:
            findings.append(f'REQUIRED_EVENT_MISSING:{event}')
    for event in prepared.contract.active_prohibitions:
        if event and event in text:
            findings.append(f'PROHIBITED_EVENT:{event}')
            continue
        if event not in by_event:
            findings.append(f'ASSURANCE:PROHIBITED_EVENT_UNVERIFIED:{event}')
        elif by_event[event]:
            findings.append(f'PROHIBITED_EVENT:{event}')
    return findings


def _paragraph_check(prepared, text, context):
    return evaluate_paragraph_topology(text, context)


def _model_prior_check(prepared, text, context):
    return audit_model_prior(text, context)


def _knowledge_check(prepared, text, context):
    findings=[]
    if context.get('unreachable_claims', 0): findings.append('KNOWLEDGE_LEAK')
    for token in getattr(prepared,'verification_guard',()):
        if token and token in text:
            marker=hashlib.sha256(token.encode('utf-8')).hexdigest()[:12]
            findings.append(f'KNOWLEDGE_LEAK:guard:{marker}')
    return findings




def _creative_search_check(prepared, text, context):
    receipt=getattr(prepared,'search_receipt',None)
    if receipt is not None and getattr(getattr(receipt,'decision',None),'path',None) is not None:
        from .creative import SearchPath
        if receipt.decision.path is SearchPath.HIGH_ASSURANCE and receipt.selected_conception is None:
            return ['ASSURANCE:CREATIVE_SEARCH_INCOMPLETE']
    return []

def _hard_user_bans_check(prepared, text, context):
    bans=tuple(context.get('hard_user_bans', ()))
    return [f'HARD_USER_BAN:{token}' for token in bans if token and token in text]


VERIFIER_REGISTRY = {
    'AUTHORITY_CONTRACT': _authority_check,
    'PARAGRAPH_TOPOLOGY': _paragraph_check,
    'MODEL_PRIOR': _model_prior_check,
    'KNOWLEDGE_REACHABILITY': _knowledge_check,
    'HARD_USER_BANS': _hard_user_bans_check,
    'CREATIVE_SEARCH_COMPLETENESS': _creative_search_check,
}

VERIFIER_VERSIONS={check_id:'1.0' for check_id in VERIFIER_REGISTRY}


def execute_required_verifiers(prepared, *, text: str, context: dict | None = None, external_observations=()) -> VerificationRecord:
    context=dict(context or {})
    external_observations=tuple(external_observations or ())
    context['_external_observations']=external_observations
    proposal_hash=hashlib.sha256(text.encode('utf-8')).hexdigest()
    required=tuple(dict.fromkeys(prepared.required_verifier_set))
    receipts=[]; failures=[]; critical_unknowns=[]; executed=[]
    for check_id in required:
        fn=VERIFIER_REGISTRY.get(check_id)
        if fn is None:
            critical_unknowns.append(f'MISSING_REQUIRED_CHECK:{check_id}')
            continue
        findings=fn(prepared,text,context)
        assurance=[x for x in findings if str(x).startswith('ASSURANCE:')]
        ordinary=[x for x in findings if x not in assurance]
        receipt=_receipt(check_id,proposal_hash,prepared.prepared_scene_hash,ordinary)
        receipts.append(receipt); executed.append(check_id); failures.extend(ordinary)
        critical_unknowns.extend(str(x).split(':',1)[1] for x in assurance)
    evidence_failures=verify_external_evidence(external_observations)
    if evidence_failures:
        failures.extend(evidence_failures)
    missing=set(required)-set(executed)
    for check_id in sorted(missing):
        marker=f'MISSING_REQUIRED_CHECK:{check_id}'
        if marker not in critical_unknowns: critical_unknowns.append(marker)
    if critical_unknowns:
        qualification=QualificationStatus.ASSURANCE_NOT_MET
    elif failures:
        qualification=QualificationStatus.FAIL
    else:
        qualification=QualificationStatus.PASS
    return VerificationRecord(
        scene_id=prepared.contract.scene_id,
        proposal_hash=proposal_hash,
        prepared_scene_hash=prepared.prepared_scene_hash,
        parent_state_version=prepared.parent_state_version,
        parent_state_hash=prepared.parent_state_hash,
        required_checks=required,
        executed_checks=tuple(executed),
        check_receipts=tuple(receipts),
        failures=tuple(dict.fromkeys(failures)),
        critical_unknowns=tuple(critical_unknowns),
        qualification=qualification,
        selected_card_ids=tuple(r.card.id for r in prepared.selection.selected),
    )


def verify_intelligence_usage(selected_cards,scene_signals:dict,proposed_changes:dict,context:dict)->list[str]:
    failures=[]; selected_ids=[c.id for c in selected_cards]; selected_set=set(selected_ids)
    high_power={'REVEAL_CAUSAL_ACCOUNTING','MYSTERY_FAIRNESS','INFORMATION_MODE_SELECTION'}
    major = scene_signals.get('major_reveal')
    grounded_major = isinstance(major, SceneSignal) and major.value and major.confidence >= 0.5 and bool(major.evidence_refs) and major.source is not SignalSource.LEGACY_RAW
    if scene_signals.get('ordinary_domestic') and not grounded_major and (len(selected_cards)>3 or any(cid in high_power for cid in selected_ids)):
        failures.append('INTELLIGENCE_OVERACTIVATION')
    elif len(selected_cards)>8: failures.append('INTELLIGENCE_OVERACTIVATION')
    if isinstance(proposed_changes,dict):
        for proposed_id in proposed_changes:
            if proposed_id not in selected_set:
                failures.append(f'INTELLIGENCE_UNSELECTED_EFFECT:{proposed_id}')
    dim_values={}
    for card in selected_cards:
        changes=proposed_changes.get(card.id,{}) if isinstance(proposed_changes,dict) else {}
        if not isinstance(changes,dict): continue
        owned=set(card.owns_dimensions); forbidden=set(card.forbidden_dimensions)
        for dim,value in changes.items():
            if dim in forbidden:
                failures.append(f'INTELLIGENCE_DIMENSION_LEAK:{card.id}:{dim}')
            elif dim not in owned:
                failures.append(f'INTELLIGENCE_UNOWNED_EFFECT:{card.id}:{dim}')
            if dim in {'speaker_knowledge','canon_truth'} and context.get('unreachable_claims',0): failures.append('KNOWLEDGE_LEAK')
            dim_values.setdefault(dim,[]).append((card.id,value))
    resolvers=set(context.get('resolved_shared_dimensions',()))
    for dim,vals in dim_values.items():
        if len(vals)>1 and len({repr(v) for _,v in vals})>1 and dim not in resolvers:
            failures.append(f'INTELLIGENCE_CONFLICT:{dim}')
    if scene_signals.get('active_misdirection') and any(cid in selected_ids for cid in {'INFORMATION_MODE_SELECTION','MYSTERY_FAIRNESS'}) and not context.get('misdirection_causal_gain',False): failures.append('MISDIRECTION_WITHOUT_VALUE')
    if 'RECURRENCE_RECODING' in selected_ids and context.get('recurrence_emphasized') and not context.get('recurrence_recoded',False): failures.append('RECURRENCE_WITHOUT_RECODING')
    missing=context.get('material_missing_card')
    if isinstance(missing,str) and missing and missing not in selected_ids: failures.append(f'INTELLIGENCE_UNDERRETRIEVAL:{missing}')
    if context.get('character_solution_diversity')==0 and 'CHARACTER_SPECIFIC_INTELLIGENCE' in selected_ids: failures.append('CHARACTER_GENERICITY')
    if context.get('payload_bloat'): failures.append('INTELLIGENCE_PAYLOAD_BLOAT')
    executed=set(context.get('executed_checks',()))
    if context.get('require_declared_checks'):
        for card in selected_cards:
            for check in card.verifier_checks:
                if check not in executed: failures.append(f'INTELLIGENCE_CHECK_NOT_EXECUTED:{card.id}:{check}')
    return list(dict.fromkeys(failures))
