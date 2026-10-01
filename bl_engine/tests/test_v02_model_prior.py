from stateful_author.surface import evaluate_paragraph_topology, parse_prose
from stateful_author.model_prior import (
    audit_model_prior, BehaviorEvidence, BehaviorOwner, ModelPriorStatus,
)
from stateful_author.contracts import CheckReceipt
from stateful_author.repair import RepairPacket, invalidate_check_receipts, failure_root_depth


def test_single_newline_staircase_is_detected():
    text='첫 문장이다.\n둘째 문장이다.\n셋째 문장이다.\n넷째 문장이다.'
    assert 'PARAGRAPH_FRAGMENTATION' in evaluate_paragraph_topology(text)


def test_long_one_sentence_paragraphs_cannot_bypass_fragmentation():
    lines=[('이 문장은 길이를 늘려도 하나의 완결된 서술 비트일 뿐이며 경계 근거가 없는 상태를 일부러 아주 길게 적어 둔 문장이다.'+str(i)) for i in range(4)]
    text='\n\n'.join(lines)
    assert 'PARAGRAPH_FRAGMENTATION' in evaluate_paragraph_topology(text)


def test_rolling_staircase_1_2_1_2_1_is_detected():
    text='하나.\n둘. 셋.\n넷.\n다섯. 여섯.\n일곱.'
    assert 'PARAGRAPH_FRAGMENTATION' in evaluate_paragraph_topology(text)


def test_no_period_fragment_staircase_is_detected():
    text='문 앞에서 멈춤\n손을 내리지 못함\n다시 시계를 봄\n아무 말도 하지 않음'
    assert 'PARAGRAPH_FRAGMENTATION' in evaluate_paragraph_topology(text)


def test_dialogue_turns_are_not_treated_as_narrative_staircase():
    text='“가.”\n“싫어.”\n“지금.”\n“안 간다.”'
    assert 'PARAGRAPH_FRAGMENTATION' not in evaluate_paragraph_topology(text)


def test_single_decisive_isolation_between_substantial_paragraphs_is_allowed():
    text='그는 봉투를 열어 내용을 읽었다. 두 번 확인하고도 손을 떼지 못했다. 종이를 다시 접었다.\n\n그는 문을 잠갔다.\n\n밖에서는 계속 차가 지나갔다. 그는 창문에서 물러나 불을 껐다. 의자에 앉아 기다렸다.'
    failures=evaluate_paragraph_topology(text, {'authorized_isolation_texts':('그는 문을 잠갔다.',)})
    assert 'PARAGRAPH_FRAGMENTATION' not in failures


def test_uniform_three_sentence_paragraphs_are_regularization_risk():
    para='하나. 둘. 셋.'
    text='\n\n'.join([para]*4)
    assert 'PARAGRAPH_REGULARIZATION' in evaluate_paragraph_topology(text)


def test_rhetorical_family_mutations_are_detected_beyond_literal_a_not_b():
    text='처음에는 피곤해서 그런 줄 알았다. 남은 것은 두려움이었다. A 때문은 아니었다. 실제로 남은 건 B였다.'
    assert 'FORMULAIC_RHETORIC' in audit_model_prior(text,{})


def test_semantic_echo_and_abstract_restatement_are_detected_as_discourse_behavior():
    text='그는 약 봉지를 그녀 쪽으로 밀었다. 그것은 그 나름의 배려를 의미했다. 불안했다. 마음이 가라앉지 않았다. 초조함이 남았다.'
    failures=audit_model_prior(text,{})
    assert 'ABSTRACT_RESTATEMENT' in failures
    assert 'SEMANTIC_ECHO' in failures


def test_closure_stack_can_confirm_affective_normalization_without_literal_phrase_dependency():
    text='그 정도면 됐다. 더 바랄 것은 없었다. 이상하게 어깨의 힘이 빠졌다. 이제 괜찮았다.'
    failures=audit_model_prior(text,{})
    assert 'AFFECTIVE_NORMALIZATION' in failures
    assert 'TERMINAL_CLOSURE_STACK' in failures


def test_boolean_functional_repetition_cannot_bypass_but_grounded_ownership_can():
    text='가. 가. 가.'
    assert 'FORMULAIC_REPETITION' in audit_model_prior(text, {'functional_repetition':True})
    evidence=BehaviorEvidence('REPETITION', BehaviorOwner.CHARACTER, ('span:1',), 'panic ritual')
    assert 'FORMULAIC_REPETITION' not in audit_model_prior(text, {'behavior_evidence':(evidence,)})


def test_repair_invalidation_discards_stale_receipts_touched_by_wording_change():
    p=CheckReceipt('PARAGRAPH_TOPOLOGY','1','h','EXECUTED','PASS',('e1',))
    k=CheckReceipt('KNOWLEDGE_REACHABILITY','1','h','EXECUTED','PASS',('e2',))
    kept=invalidate_check_receipts((p,k), {'WORDING','PARAGRAPH_STRUCTURE'})
    assert [x.check_id for x in kept] == ['KNOWLEDGE_REACHABILITY']
    assert failure_root_depth('PARAGRAPH_FRAGMENTATION', repeat_count=2) == 'DISCOURSE'
