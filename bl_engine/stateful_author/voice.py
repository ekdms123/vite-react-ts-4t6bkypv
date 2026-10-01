from __future__ import annotations
from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class VoiceState:
    attention_habits: frozenset[str] = field(default_factory=frozenset)
    judgment_logic: frozenset[str] = field(default_factory=frozenset)
    reality_anchors: frozenset[str] = field(default_factory=frozenset)
    emotional_evasion: frozenset[str] = field(default_factory=frozenset)
    humor_mechanisms: frozenset[str] = field(default_factory=frozenset)
    abstraction_band: str | None = None
    lyric_return_path: str | None = None

    def __post_init__(self):
        for name in ('attention_habits','judgment_logic','reality_anchors','emotional_evasion','humor_mechanisms'):
            object.__setattr__(self, name, frozenset(getattr(self, name)))


@dataclass(frozen=True)
class VoiceCheckpoint:
    attention_habits: frozenset[str] = field(default_factory=frozenset)
    judgment_logic: frozenset[str] = field(default_factory=frozenset)
    reality_anchors: frozenset[str] = field(default_factory=frozenset)
    emotional_evasion: frozenset[str] = field(default_factory=frozenset)
    humor_mechanisms: frozenset[str] = field(default_factory=frozenset)
    pressure: str = 'LOW'
    generic_narrator: bool = False
    paragraph_fragmentation: bool = False
    narrative_mode: str = 'SCENE'

    def __post_init__(self):
        for name in ('attention_habits','judgment_logic','reality_anchors','emotional_evasion','humor_mechanisms'):
            object.__setattr__(self, name, frozenset(getattr(self, name)))


def _overlap(base: frozenset[str], observed: frozenset[str]) -> float:
    if not base:
        return 1.0
    return len(base & observed) / len(base)


def evaluate_voice_checkpoint(base: VoiceState, cp: VoiceCheckpoint) -> list[str]:
    failures: list[str] = []
    scores = {
        'attention': _overlap(base.attention_habits, cp.attention_habits),
        'judgment': _overlap(base.judgment_logic, cp.judgment_logic),
        'emotion': _overlap(base.emotional_evasion, cp.emotional_evasion),
    }
    strong = sum(score >= 0.25 for score in scores.values())
    avg = sum(scores.values()) / 3
    if cp.generic_narrator or strong < 2 or avg < 0.30:
        failures.append('VOICE_DRIFT')
    if base.reality_anchors and not (base.reality_anchors & cp.reality_anchors):
        failures.append('REALITY_ANCHOR_LOSS')
    return failures


_GENERIC_EMOTIONAL = re.compile(r'(모든 것이|이미 .*시작|운명|이야기가 .*문|끝나 버린|돌아갈 수 없|무언가가 일어난|전부 끝)', re.IGNORECASE)


def portable_line_risk(line: str, context_tokens: set[str]) -> bool:
    # Context tokens reduce risk only when the line contains more than one concrete
    # context anchor; appending a single token must not neutralize a generic formula.
    matches = sum(1 for tok in context_tokens if tok and tok in line)
    generic = bool(_GENERIC_EMOTIONAL.search(line))
    return generic and matches < 2
