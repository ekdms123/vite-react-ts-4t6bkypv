from __future__ import annotations
from dataclasses import dataclass, field

_RECOVERY=('LOCAL_REPAIR','RELATION_REPAIR','DISTINCTION_RESCAN','GROUND_REFRESH','ANCHOR_RELOAD','STRATEGY_TRANSFORMATION','HUMAN_ESCALATION')


def repair_scope(code:str,repeat_count:int)->str:
    if repeat_count>=3: return 'ARCHITECTURE'
    if repeat_count==2: return 'VOICE_STATE' if code in {'VOICE_DRIFT','REALITY_ANCHOR_LOSS','MODEL_PRIOR_REVERSION'} else 'WRITER_PACKET'
    if code in {'VOICE_DRIFT','REALITY_ANCHOR_LOSS','MODEL_PRIOR_REVERSION'}: return 'SCENE'
    known_local={'PARAGRAPH_FRAGMENTATION','CLOSURE_STACKING','REDUNDANT_MEANING_RECOVERY'}
    return 'PARAGRAPH' if code in known_local else 'SCENE'

@dataclass
class FailureTracker:
    strategies: dict[str,list[str]] = field(default_factory=dict)
    def next_strategy(self,signature:str)->str:
        used=self.strategies.setdefault(signature,[])
        if len(set(used))>=3: return 'HUMAN_ESCALATION'
        for s in _RECOVERY:
            if s not in used: return s
        return 'HUMAN_ESCALATION'
    def record(self,signature:str,strategy:str)->None:
        used=self.strategies.setdefault(signature,[])
        if used and used[-1]==strategy:
            raise ValueError(f'REPEATED_STRATEGY_FOR_FAILURE:{signature}:{strategy}')
        used.append(strategy)
