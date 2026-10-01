from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class EvidenceType(str, Enum):
    USER_CANON = 'USER_CANON'
    TEXT_OBSERVED = 'TEXT_OBSERVED'
    DERIVED_HIGH_CONFIDENCE = 'DERIVED_HIGH_CONFIDENCE'
    WORKING_HYPOTHESIS = 'WORKING_HYPOTHESIS'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True)
class FactRecord:
    key: str
    value: object
    evidence_type: EvidenceType
    confidence: float
    evidence_refs: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()

    def __post_init__(self):
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError('CONFIDENCE_OUT_OF_RANGE')
        object.__setattr__(self, 'evidence_refs', tuple(self.evidence_refs))
        object.__setattr__(self, 'depends_on', tuple(self.depends_on))


_ALLOWED = {EvidenceType.USER_CANON, EvidenceType.TEXT_OBSERVED, EvidenceType.DERIVED_HIGH_CONFIDENCE}
_MIN_CONFIDENCE = {
    EvidenceType.USER_CANON: 1.0,
    EvidenceType.TEXT_OBSERVED: 0.5,
    EvidenceType.DERIVED_HIGH_CONFIDENCE: 0.8,
}


def select_writer_facts(facts: list[FactRecord], *, include_unknowns: bool = False) -> dict:
    rank = {EvidenceType.USER_CANON: 3, EvidenceType.TEXT_OBSERVED: 2, EvidenceType.DERIVED_HIGH_CONFIDENCE: 1}
    selected: dict[str, tuple[int, object, FactRecord]] = {}
    unknowns: list[str] = []
    for fact in facts:
        if fact.evidence_type is EvidenceType.UNKNOWN:
            if include_unknowns and fact.key not in unknowns:
                unknowns.append(fact.key)
            continue
        if fact.evidence_type not in _ALLOWED or fact.confidence < _MIN_CONFIDENCE[fact.evidence_type]:
            continue
        if fact.evidence_type in {EvidenceType.TEXT_OBSERVED, EvidenceType.DERIVED_HIGH_CONFIDENCE} and not fact.evidence_refs:
            continue
        r = rank[fact.evidence_type]
        if fact.key in selected:
            pr, pv, pf = selected[fact.key]
            if r == pr and pv != fact.value:
                raise ValueError(f'PROVENANCE_CONFLICT:{fact.key}')
            if r < pr:
                continue
        selected[fact.key] = (r, fact.value, fact)
    out = {k: v for k, (_, v, _) in selected.items()}
    if include_unknowns:
        out['__unknowns__'] = tuple(unknowns)
    return out
