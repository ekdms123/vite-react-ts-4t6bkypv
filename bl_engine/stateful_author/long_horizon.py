from dataclasses import dataclass
from .voice import VoiceState, VoiceCheckpoint, evaluate_voice_checkpoint


@dataclass(frozen=True)
class LongHorizonResult:
    failures: list[str]
    vector: dict[str, float]


def _continuity_ratio(base, checkpoints, attr: str) -> float:
    if not checkpoints:
        return 1.0
    vals=[]
    for cp in checkpoints:
        observed=getattr(cp,attr)
        if not base:
            vals.append(1.0)
        else:
            overlap=len(base & observed)/len(base)
            # Long-horizon identity is conditional, not a quota requiring every
            # baseline token at every checkpoint. Material retention begins at 25%.
            vals.append(1.0 if overlap >= 0.25 else overlap)
    return sum(vals)/len(vals)


def evaluate_long_horizon(base: VoiceState, checkpoints: list[VoiceCheckpoint]) -> LongHorizonResult:
    failures=[]
    per_cp=[evaluate_voice_checkpoint(base,cp) for cp in checkpoints]
    if checkpoints and any(code in per_cp[-1] for code in ('VOICE_DRIFT','REALITY_ANCHOR_LOSS')):
        failures.append('LATE_VOICE_REVERSION')
    if len(checkpoints) > 2 and any(any(code in f for code in ('VOICE_DRIFT','REALITY_ANCHOR_LOSS')) for f in per_cp[1:-1]):
        failures.append('MID_HORIZON_VOICE_REVERSION')
    if any(cp.paragraph_fragmentation for cp in checkpoints):
        failures.append('LONG_HORIZON_SURFACE_DRIFT')
    if any(cp.narrative_mode == 'BIOGRAPHICAL_SUMMARY' for cp in checkpoints):
        failures.append('LONG_HORIZON_MEMORY_DRIFT')
    voice_components=[_continuity_ratio(getattr(base,a),checkpoints,a) for a in ('attention_habits','judgment_logic','emotional_evasion')]
    voice=sum(voice_components)/len(voice_components) if voice_components else 1.0
    reality=_continuity_ratio(base.reality_anchors,checkpoints,'reality_anchors')
    return LongHorizonResult(list(dict.fromkeys(failures)), {
        'voice_continuity':round(voice,3),
        'reality_anchor_continuity':round(reality,3),
        'surface_continuity':0.0 if any(cp.paragraph_fragmentation for cp in checkpoints) else 1.0,
        'mode_continuity':0.0 if any(cp.narrative_mode=='BIOGRAPHICAL_SUMMARY' for cp in checkpoints) else 1.0,
    })
