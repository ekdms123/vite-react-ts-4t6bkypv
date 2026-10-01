from __future__ import annotations
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from stateful_author.executability import load_execution_ledger,contract_coverage
from stateful_author.intelligence import load_intelligence_library, SceneSignal, SignalSource
from stateful_author.runtime import SceneContract,prepare_scene,verify_proposal,state_hash
from stateful_author.provenance import FactRecord,EvidenceType,select_writer_facts
from stateful_author.surface import evaluate_paragraph_topology
from stateful_author.model_prior import audit_model_prior
from stateful_author.commercial import evaluate_commercial_arc
from stateful_author.serial import EpisodeDelta,PressureVector
from stateful_author.reader import ReaderModel

LIB=load_intelligence_library(ROOT/'author/intelligence/cards')
base_state={
 '_version':'v1',
 'voice_state':{'attention_habits':['cost','body'],'judgment_logic':['usable_or_not'],'reality_anchors':['money','body']},
 'narrative_state':{
   'knowledge_by_actor':{'A':['door_locked']},'active_knowledge_by_actor':{'A':['door_locked']},
   'beliefs_by_actor':{'A':{'visitor':'late'}},'relevant_unknowns':['culprit'],
   'objective_affordances':['front','secret_exit'],'perceived_affordances_by_actor':{'A':['front']},
   'hidden_master_plan':'SECRET'
 },
 'reader_model':ReaderModel(active_questions=('Who?',)),
 'relationship_state':{'distance':'guarded'}
}
contract=SceneContract('soak','A','write ordinary scene',parent_state_version='v1',narrator_mode='FOCAL_CLOSE',parent_state_hash=state_hash(base_state))
prepared=prepare_scene(contract,base_state,LIB,scene_signals={})
qualification=verify_proposal(prepared,text='그는 문고리를 잡았다. 손바닥에 금속의 찬 기운이 남았다.',context={})
reveal_signal=SceneSignal('major_reveal',True,.95,('scene:e1',),SignalSource.TEXT_OBSERVED,'HIGH')
high=prepare_scene(SceneContract('reveal','A','write reveal',parent_state_version='v1',parent_state_hash=state_hash(base_state)),base_state,LIB,scene_signals={'major_reveal':reveal_signal})
high_q=verify_proposal(high,text='문장.',context={})
low_fact=select_writer_facts([FactRecord('x','bad',EvidenceType.DERIVED_HIGH_CONFIDENCE,.95)])
paragraph_mutations={
 'single_newline':evaluate_paragraph_topology('하나.\n둘.\n셋.\n넷.'),
 'rolling':evaluate_paragraph_topology('하나.\n둘. 셋.\n넷.\n다섯. 여섯.\n일곱.'),
 'regularized':evaluate_paragraph_topology('\n\n'.join(['하나. 둘. 셋.']*4)),
}
rhetoric=audit_model_prior('처음에는 A라 여겼다. 남은 것은 B였다. A 때문은 아니었다. 실제로 남은 건 B였다.',{})
nontransform=evaluate_commercial_arc([
 {'delta':EpisodeDelta(metabolism='INHABIT'),'pressure':PressureVector()},
 {'delta':EpisodeDelta(metabolism='RECOVER'),'pressure':PressureVector()},
],[])
entries=load_execution_ledger(ROOT/'verify/EXECUTION_LEDGER.json')
coverage=contract_coverage(ROOT,entries)
blob=json.dumps(prepared.writer_packet,ensure_ascii=False)
report={
 'schema_version':'0.2',
 'ordinary_qualification':qualification.qualification.value,
 'required_checks':list(qualification.required_checks),'executed_checks':list(qualification.executed_checks),
 'high_assurance_without_candidates':high_q.qualification.value,
 'oracle_leak_absent':all(x not in blob for x in ('SECRET','secret_exit','correct_answer','reader_model','narrative_state')),
 'narrator_mode':prepared.writer_packet['scene']['narrator_mode'],
 'low_confidence_or_ungrounded_fact_selected':low_fact,
 'paragraph_mutations':paragraph_mutations,'rhetorical_mutation_findings':rhetoric,
 'nontransformative_failures':nontransform.failures,
 'contract_coverage':coverage.to_dict(),
 'literary_validation':'ASSURANCE_NOT_MET'
}
out=ROOT/'verify/MASTER_SOAK_RESULTS.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(out)
