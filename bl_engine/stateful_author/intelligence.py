from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from copy import deepcopy
import json


@dataclass(frozen=True)
class IntelligenceCard:
    id: str
    version: int
    purpose: str
    trigger: dict
    preconditions: tuple[str, ...]
    owns_dimensions: tuple[str, ...]
    forbidden_dimensions: tuple[str, ...]
    context_requirements: dict
    writer_payload: dict
    suppress_when: tuple[str, ...]
    verifier_checks: tuple[str, ...]


class SignalSource(str, Enum):
    USER = 'USER'
    STATE = 'STATE'
    TEXT_OBSERVED = 'TEXT_OBSERVED'
    DERIVED = 'DERIVED'
    LEGACY_RAW = 'LEGACY_RAW'


@dataclass(frozen=True)
class SceneSignal:
    id: str
    value: bool
    confidence: float = 0.0
    evidence_refs: tuple[str, ...] = ()
    source: SignalSource = SignalSource.LEGACY_RAW
    criticality: str = 'NORMAL'

    def __post_init__(self):
        if not 0 <= float(self.confidence) <= 1:
            raise ValueError('SIGNAL_CONFIDENCE_OUT_OF_RANGE')
        object.__setattr__(self, 'evidence_refs', tuple(self.evidence_refs))
        if not isinstance(self.source, SignalSource):
            object.__setattr__(self, 'source', SignalSource(str(self.source)))


@dataclass(frozen=True)
class RankedCard:
    card: IntelligenceCard
    score: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SelectionResult:
    selected: tuple[RankedCard, ...]
    conflicts: tuple[str, ...] = ()
    suppressed: tuple[str, ...] = ()


@dataclass(frozen=True)
class AuthorizedIntelligencePayload:
    id: str
    version: int
    guidance: tuple[str, ...]
    artifact: tuple[tuple[str, str], ...] = ()


SELECTABLE_CARD_IDS = frozenset({
    'PERCEPTION_SELECTION', 'CHARACTER_SPECIFIC_INTELLIGENCE',
    'RELATIONSHIP_EVIDENCE', 'DIALOGUE_AS_RELATIONAL_ACTION',
    'EMOTIONAL_AVOIDANCE', 'EMBODIMENT_AND_REALITY',
    'HUMOR_COGNITION', 'INFORMATION_MODE_SELECTION', 'MYSTERY_FAIRNESS',
    'REVEAL_CAUSAL_ACCOUNTING', 'RECURRENCE_RECODING',
    'MEMORY_PRESENT_RELEVANCE', 'PRESSURE_RESPONSE',
})

REQUIRED_FIELDS = {
    'id', 'purpose', 'trigger', 'preconditions', 'owns_dimensions',
    'forbidden_dimensions', 'context_requirements', 'writer_payload',
    'suppress_when', 'verifier_checks',
}

KNOWN_VERIFIER_CHECKS = frozenset({
    'CHARACTER_GENERICITY', 'KNOWLEDGE_LEAK', 'MODEL_PRIOR_REVERSION_AUDIT',
    'INTELLIGENCE_DIMENSION_LEAK', 'MISDIRECTION_WITHOUT_VALUE',
    'NARRATIVE_MODE_DRIFT', 'RECURRENCE_WITHOUT_RECODING',
    'VOICE_DRIFT', 'REALITY_ANCHOR_LOSS',
})

HIGH_IMPACT_SIGNALS = frozenset({
    'major_reveal', 'active_misdirection', 'relationship_pivot',
    'consequential_decision', 'threshold_pressure',
})
HIGH_IMPACT_CARDS = frozenset({
    'REVEAL_CAUSAL_ACCOUNTING', 'MYSTERY_FAIRNESS',
    'INFORMATION_MODE_SELECTION', 'RELATIONSHIP_EVIDENCE',
    'CHARACTER_SPECIFIC_INTELLIGENCE',
})

CONTRADICTION_PAIRS = (
    ('major_reveal', 'minor_reveal_without_accounting_need'),
    ('relationship_pivot', 'no_relationship_material'),
    ('recurrence_recoded', 'recurrence_unchanged'),
    ('humor_opportunity', 'no_character_owned_humor'),
)


def _from_manifest(obj: dict) -> IntelligenceCard:
    missing = REQUIRED_FIELDS - obj.keys()
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    return IntelligenceCard(
        id=str(obj.get('id', '')),
        version=int(obj.get('version', 1)),
        purpose=str(obj.get('purpose', '')),
        trigger=dict(obj.get('trigger', {})),
        preconditions=tuple(obj.get('preconditions', [])),
        owns_dimensions=tuple(obj.get('owns_dimensions', [])),
        forbidden_dimensions=tuple(obj.get('forbidden_dimensions', [])),
        context_requirements=dict(obj.get('context_requirements', {})),
        writer_payload=dict(obj.get('writer_payload', {})),
        suppress_when=tuple(obj.get('suppress_when', [])),
        verifier_checks=tuple(obj.get('verifier_checks', [])),
    )


def validate_card(card: IntelligenceCard) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        value = getattr(card, field)
        if value is None or value == '' or (field in {'trigger', 'context_requirements', 'writer_payload'} and not isinstance(value, dict)):
            errors.append(f'CARD_FIELD_MISSING:{field}')
    if not card.id:
        errors.append('CARD_FIELD_MISSING:id') if 'CARD_FIELD_MISSING:id' not in errors else None
    if card.id and card.id not in SELECTABLE_CARD_IDS:
        # Permit synthetic cards in direct validation tests, but library loading enforces known set.
        pass
    trig = card.trigger
    if not isinstance(trig, dict) or any(k not in {'any','all'} for k in trig):
        errors.append('CARD_TRIGGER_INVALID')
    else:
        for k in ('any','all'):
            value = trig.get(k, [])
            if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
                errors.append('CARD_TRIGGER_INVALID')
                break
    for name, dims in (('owns_dimensions', card.owns_dimensions), ('forbidden_dimensions', card.forbidden_dimensions)):
        if len(set(dims)) != len(dims):
            errors.append(f'CARD_DIMENSION_DUPLICATE:{name}')
    overlap = set(card.owns_dimensions) & set(card.forbidden_dimensions)
    for dim in sorted(overlap):
        errors.append(f'CARD_AUTHORITY_OVERLAP:{dim}')
    req = card.context_requirements
    if not isinstance(req.get('required', []), list) or not isinstance(req.get('optional', []), list):
        errors.append('CARD_CONTEXT_REQUIREMENTS_INVALID')
    max_items = card.writer_payload.get('max_items')
    if not isinstance(max_items, int) or not 1 <= max_items <= 6:
        errors.append('CARD_PAYLOAD_LIMIT_INVALID')
    if card.writer_payload.get('form') != 'decision_guidance':
        errors.append('CARD_PAYLOAD_FORM_INVALID')
    unknown_checks = [x for x in card.verifier_checks if x not in KNOWN_VERIFIER_CHECKS]
    for x in unknown_checks:
        errors.append(f'CARD_VERIFIER_UNKNOWN:{x}')
    return list(dict.fromkeys(errors))


def load_intelligence_library(path: Path) -> dict[str, IntelligenceCard]:
    library: dict[str, IntelligenceCard] = {}
    parsed: list[tuple[Path, IntelligenceCard]] = []
    seen: set[str] = set()
    for file in sorted(path.glob('*.json')):
        card = _from_manifest(json.loads(file.read_text(encoding='utf-8')))
        errors = validate_card(card)
        if errors:
            raise ValueError(f'{file.name}: {errors}')
        if card.id in seen:
            raise ValueError(f'duplicate card id: {card.id}')
        seen.add(card.id)
        parsed.append((file, card))
    for file, card in parsed:
        if card.id not in SELECTABLE_CARD_IDS:
            raise ValueError(f'unknown card id: {card.id}')
        library[card.id] = card
    return library


def _get_path(state: dict, path: str):
    cur = state
    for part in path.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _bool_value(value) -> bool:
    if isinstance(value, SceneSignal):
        return bool(value.value)
    return bool(value)


def _normalize_signals(scene_signals: dict) -> dict[str, SceneSignal]:
    out = {}
    for key, value in scene_signals.items():
        if isinstance(value, SceneSignal):
            out[key] = value
        else:
            out[key] = SceneSignal(key, bool(value), 0.0, (), SignalSource.LEGACY_RAW, 'NORMAL')
    return out


def _triggered(card: IntelligenceCard, scene_signals: dict) -> bool:
    any_keys = card.trigger.get('any', [])
    all_keys = card.trigger.get('all', [])
    any_ok = True if not any_keys else any(_bool_value(scene_signals.get(k)) for k in any_keys)
    all_ok = all(_bool_value(scene_signals.get(k)) for k in all_keys)
    return any_ok and all_ok


def _preconditions_met(card: IntelligenceCard, scene_signals: dict, state: dict) -> bool:
    for cond in card.preconditions:
        if not _bool_value(scene_signals.get(cond)) and _get_path(state, cond) is None:
            return False
    for path in card.context_requirements.get('required', []):
        value = _get_path(state, path)
        if value is None or value == [] or value == {} or value == '':
            return False
    return True


def select_intelligence_cards(scene_signals: dict, state: dict, library: dict[str, IntelligenceCard]) -> list[IntelligenceCard]:
    """Legacy-compatible boolean selector. New runtime paths use ranked grounded selection."""
    selected: list[IntelligenceCard] = []
    for card in library.values():
        if not _triggered(card, scene_signals):
            continue
        if any(_bool_value(scene_signals.get(flag)) for flag in card.suppress_when):
            continue
        if not _preconditions_met(card, scene_signals, state):
            continue
        selected.append(card)
    return selected


def _signal_is_grounded(sig: SceneSignal) -> bool:
    if not sig.value:
        return False
    if sig.source in {SignalSource.USER, SignalSource.STATE, SignalSource.TEXT_OBSERVED}:
        return sig.confidence >= 0.5 and bool(sig.evidence_refs)
    if sig.source is SignalSource.DERIVED:
        return sig.confidence >= 0.8 and bool(sig.evidence_refs)
    return False


def _conflicts(signals: dict[str, SceneSignal]) -> tuple[str, ...]:
    out=[]
    for a,b in CONTRADICTION_PAIRS:
        sa,sb=signals.get(a),signals.get(b)
        if sa and sb and sa.value and sb.value and _signal_is_grounded(sa) and _signal_is_grounded(sb):
            out.append(f'SIGNAL_CONTRADICTION:{a}:{b}')
    return tuple(out)


def select_intelligence_cards_ranked(scene_signals: dict, state: dict, library: dict[str, IntelligenceCard], *, limit: int = 8) -> SelectionResult:
    signals=_normalize_signals(scene_signals)
    conflicts=_conflicts(signals)
    ranked=[]; suppressed=[]
    for card in library.values():
        if not _triggered(card, signals):
            continue
        matched=[k for k in card.trigger.get('any',[]) if k in signals and signals[k].value]
        matched += [k for k in card.trigger.get('all',[]) if k in signals and signals[k].value]
        if any(_bool_value(signals.get(flag)) for flag in card.suppress_when):
            suppressed.append(card.id); continue
        if not _preconditions_met(card, signals, state):
            suppressed.append(card.id); continue
        if card.id in HIGH_IMPACT_CARDS and any(k in HIGH_IMPACT_SIGNALS for k in matched):
            if not any(_signal_is_grounded(signals[k]) for k in matched if k in HIGH_IMPACT_SIGNALS):
                suppressed.append(card.id); continue
        confs=[signals[k].confidence for k in matched if k in signals]
        grounded=sum(1 for k in matched if k in signals and _signal_is_grounded(signals[k]))
        critical=max((2 if signals[k].criticality.upper()=='HIGH' else 1 if signals[k].criticality.upper()=='MEDIUM' else 0) for k in matched if k in signals) if matched else 0
        score=grounded*3.0 + (max(confs) if confs else 0.0)*2.0 + len(set(matched))*0.6 + critical
        necessity_boost = {
            'REVEAL_CAUSAL_ACCOUNTING': 5.0 if 'major_reveal' in matched else 0.0,
            'RELATIONSHIP_EVIDENCE': 4.0 if 'relationship_pivot' in matched else 0.0,
            'PRESSURE_RESPONSE': 3.5 if 'high_pressure' in matched or 'threshold_pressure' in matched else 0.0,
            'MEMORY_PRESENT_RELEVANCE': 3.0 if 'flashback' in matched else 0.0,
            'RECURRENCE_RECODING': 3.0 if 'recurrence_return' in matched or 'meaningful_return' in matched else 0.0,
            'MYSTERY_FAIRNESS': 3.0 if 'mystery_evidence_conflict' in matched or 'active_misdirection' in matched else 0.0,
            'INFORMATION_MODE_SELECTION': 3.0 if 'information_asymmetry' in matched or 'mystery_evidence_conflict' in matched else 0.0,
            'CHARACTER_SPECIFIC_INTELLIGENCE': 3.0 if 'consequential_decision' in matched else 0.0,
            'DIALOGUE_AS_RELATIONAL_ACTION': 1.0 if 'dialogue_conflict' in matched else 0.0,
            'EMBODIMENT_AND_REALITY': 0.8,
            'EMOTIONAL_AVOIDANCE': 0.8,
            'PERCEPTION_SELECTION': 0.5,
            'HUMOR_COGNITION': 0.0,
        }.get(card.id, 0.0)
        score += necessity_boost
        reasons=tuple([f'trigger:{k}' for k in sorted(set(matched))] + ([f'grounded:{grounded}'] if grounded else ['legacy_or_unverified']))
        ranked.append(RankedCard(card,score,reasons))
    ranked.sort(key=lambda r:(-r.score,r.card.id))
    effective_conflicts=list(conflicts)
    critical_ranked=[]
    for item in ranked:
        trig_ids=[r.split(':',1)[1] for r in item.reasons if r.startswith('trigger:')]
        if any(k in signals and _signal_is_grounded(signals[k]) and signals[k].criticality.upper()=='HIGH' for k in trig_ids):
            critical_ranked.append(item)
    if len(critical_ranked) > limit:
        effective_conflicts.append(f'INTELLIGENCE_CAPACITY_CONFLICT:{len(critical_ranked)}>{limit}')
    return SelectionResult(tuple(ranked[:max(0,limit)]), tuple(effective_conflicts), tuple(sorted(set(suppressed))))


def pull_card_context(card: IntelligenceCard, state: dict) -> dict:
    pulled: dict = {}
    paths = list(card.context_requirements.get('required', [])) + list(card.context_requirements.get('optional', []))
    for path in paths:
        value = _get_path(state, path)
        if value is not None:
            pulled[path] = deepcopy(value)
    return pulled


def _join_values(value) -> str:
    if isinstance(value, dict):
        return ', '.join(map(str, sorted(value.keys(), key=str)))
    if isinstance(value, (set, frozenset)):
        return ', '.join(map(str, sorted(value, key=str)))
    if isinstance(value, (list, tuple)):
        return ', '.join(map(str, value))
    return str(value)


def _guidance_for(card_id: str, context: dict, signals: dict) -> list[str]:
    attention = _join_values(context.get('voice_state.attention_habits', 'established attention'))
    judgment = _join_values(context.get('voice_state.judgment_logic', 'established judgment'))
    guides = {
        'PERCEPTION_SELECTION': [f'Filter selected detail through the focal attention pattern: {attention}.', 'Allow focal-owned lived detail even when it is not payoff machinery; reject neutral inventory.'],
        'CHARACTER_SPECIFIC_INTELLIGENCE': [f'Let the choice emerge from this character’s attention ({attention}) and judgment logic ({judgment}), not an author-optimal solution.', 'Preserve reachable knowledge, perceived options, bias, and local rationality.'],
        'RELATIONSHIP_EVIDENCE': ['Ground relationship change in prior behavior, access, boundary, labor, routine, cost, obligation, distance, or willingness.', 'Treat changed relational permission as more important than a declaration that merely names the relationship.'],
        'DIALOGUE_AS_RELATIONAL_ACTION': ['Let consequential dialogue alter information, status, distance, consent, avoidance, control, obligation, common ground, or the interaction frame.', 'Preserve ordinary banter, repair, echo, or silence when functionally owned; not every line needs a state change.'],
        'EMOTIONAL_AVOIDANCE': ['Route unresolved emotion through the focal character’s current coping/avoidance policy before forcing abstract explanation.', 'Do not force delayed naming as a universal rule; name emotion when recognition itself changes state.'],
        'EMBODIMENT_AND_REALITY': ['Keep cognition attached to body, object, cost, tool, space, or environment when selected by focal attention.', 'Concrete reality may be non-instrumental; do not require every object to become payoff or symbol.'],
        'HUMOR_COGNITION': ['If humor occurs, make it a character-owned frame transfer, inference, register shift, or relational move rather than a detached punchline.', 'Do not give every character the same humorous reasoning or trade pressure for wit.'],
        'INFORMATION_MODE_SELECTION': ['Distinguish runtime truth from in-world evidence, and natural limitation from opacity, deception, rumor, memory, or inference.', 'Keep focal and reader knowledge boundaries intact.'],
        'MYSTERY_FAIRNESS': ['Maintain multiple plausible reader models only when evidence supports them; fairness includes activation and retrievability, not clue existence alone.', 'Do not hide information solely to preserve mystery and do not make the problem untractable.'],
        'REVEAL_CAUSAL_ACCOUNTING': ['Route the reveal by type; preserve why the earlier model was plausible and keep prior evidence true or explainable.', 'For major reveals, change causal/option/reader meaning; do not force local minor reveals into architecture events.'],
        'RECURRENCE_RECODING': ['Promote a return only through changed function or meaning; recognition alone is not payoff.', 'Do not turn every repeated object into a planned motif.'],
        'MEMORY_PRESENT_RELEVANCE': ['Expand only past material actively producing present reaction, belief, choice, or consequence.', 'Separate stored knowledge, current activation, reconstructed memory, and disclosure.'],
        'PRESSURE_RESPONSE': [f'Under acute pressure, narrow optional cognition while preserving the character’s attention ({attention}) and judgment ({judgment}).', 'Pressure may compress or distort processing but does not mandate short sentences or erase identity.'],
    }
    return guides.get(card_id, ['Apply only the selected author decision procedure to the current scene.'])


def compile_intelligence_payload(card: IntelligenceCard, context: dict, scene_signals: dict) -> dict:
    guidance = _guidance_for(card.id, context, scene_signals)
    return {'id': card.id, 'guidance': guidance[: card.writer_payload['max_items']]}


def compile_authorized_payload(card: IntelligenceCard, context: dict, scene_signals: dict) -> AuthorizedIntelligencePayload:
    payload=compile_intelligence_payload(card,context,scene_signals)
    scene_line = ''
    if card.id == 'REVEAL_CAUSAL_ACCOUNTING':
        beliefs = _join_values(context.get('narrative_state.beliefs', ''))
        loops = _join_values(context.get('open_loops', ''))
        if beliefs or loops:
            scene_line = f'Current model material: beliefs [{beliefs}] / live questions [{loops}]. Preserve only what the scene can support.'
    elif card.id == 'RELATIONSHIP_EVIDENCE':
        rel = _join_values(context.get('relationship_state', ''))
        if rel:
            scene_line = f'Current relationship evidence/state: {rel}. Change permissions only through observable scene evidence.'
    elif card.id == 'CHARACTER_SPECIFIC_INTELLIGENCE':
        att = _join_values(context.get('voice_state.attention_habits', ''))
        judge = _join_values(context.get('voice_state.judgment_logic', ''))
        if att or judge:
            scene_line = f'Current focal policy: attention [{att}] / judgment [{judge}].'
    elif card.id == 'RECURRENCE_RECODING':
        rec = _join_values(context.get('relevant_recurrences', ''))
        if rec:
            scene_line = f'Relevant prior recurrence state: {rec}. Emphasize only a changed function or meaning.'
    elif card.id == 'MEMORY_PRESENT_RELEVANCE':
        consequence = _join_values(context.get('narrative_state.present_consequence', ''))
        if consequence:
            scene_line = f'Present consequence pulling the memory forward: {consequence}.'
    guidance = list(payload['guidance'])
    if scene_line:
        guidance = [scene_line] + guidance
    guidance = guidance[: card.writer_payload['max_items']]
    artifact = tuple((k, _join_values(v)) for k,v in sorted(context.items()) if k in card.context_requirements.get('required',[]) + card.context_requirements.get('optional',[]))
    return AuthorizedIntelligencePayload(card.id,card.version,tuple(guidance),artifact[:6])


@dataclass(frozen=True)
class IntelligenceSequenceResult:
    activations: tuple[tuple[str, ...], ...]
    failures: list[str]


def evaluate_intelligence_sequence(sequence: list[dict], state: dict, library: dict[str, IntelligenceCard]) -> IntelligenceSequenceResult:
    activations=[]; failures=[]
    for signals in sequence:
        selected=select_intelligence_cards(signals,state,library)
        ids=tuple(card.id for card in selected); activations.append(ids)
        if signals.get('ordinary_domestic') and any(cid in ids for cid in {'REVEAL_CAUSAL_ACCOUNTING','MYSTERY_FAIRNESS','INFORMATION_MODE_SELECTION'}):
            failures.append('INTELLIGENCE_OVERACTIVATION')
    return IntelligenceSequenceResult(tuple(activations),list(dict.fromkeys(failures)))
