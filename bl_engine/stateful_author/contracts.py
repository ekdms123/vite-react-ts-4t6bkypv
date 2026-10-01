from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class QualificationStatus(str, Enum):
    PASS = 'PASS'
    FAIL = 'FAIL'
    ASSURANCE_NOT_MET = 'ASSURANCE_NOT_MET'

ALLOWED_TRANSFORMATION_AUTHORITIES = frozenset({
    'USER','CANON','STATE','SCENE','SOURCE','APPROVED_STYLE','COMPILER_VALIDATED','VERIFIED_EVIDENCE',
})


@dataclass(frozen=True)
class TransformationRecord:
    dimension: str
    key: str
    before: object
    after: object
    reason: str
    authority: str
    evidence_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, 'evidence_refs', tuple(self.evidence_refs))
        object.__setattr__(self, 'provenance_refs', tuple(self.provenance_refs))
        object.__setattr__(self, 'dependencies', tuple(self.dependencies))

    def validate(self) -> None:
        if not self.dimension or not self.key or not str(self.reason).strip() or not str(self.authority).strip():
            raise ValueError('STATE_DELTA_TRANSFORMATION_INVALID')
        if self.authority not in ALLOWED_TRANSFORMATION_AUTHORITIES:
            raise ValueError('STATE_DELTA_AUTHORITY_INVALID')
        # Durable transformations need a concrete evidentiary/provenance anchor.
        if not self.evidence_refs and not self.provenance_refs:
            raise ValueError('STATE_DELTA_TRANSFORMATION_INVALID')


@dataclass(frozen=True)
class StateDelta:
    proposal_hash: str = ''
    fact_delta: tuple[TransformationRecord, ...] = ()
    evidence_delta: tuple[TransformationRecord, ...] = ()
    knowledge_delta: tuple[TransformationRecord, ...] = ()
    belief_delta: tuple[TransformationRecord, ...] = ()
    memory_delta: tuple[TransformationRecord, ...] = ()
    self_model_delta: tuple[TransformationRecord, ...] = ()
    relationship_delta: tuple[TransformationRecord, ...] = ()
    affordance_delta: tuple[TransformationRecord, ...] = ()
    world_delta: tuple[TransformationRecord, ...] = ()
    open_loop_delta: tuple[TransformationRecord, ...] = ()
    recurrence_delta: tuple[TransformationRecord, ...] = ()
    reader_delta: tuple[TransformationRecord, ...] = ()
    serial_delta: tuple[TransformationRecord, ...] = ()
    voice_delta: tuple[TransformationRecord, ...] = ()

    _FIELDS = (
        'fact_delta','evidence_delta','knowledge_delta','belief_delta','memory_delta','self_model_delta',
        'relationship_delta','affordance_delta','world_delta','open_loop_delta','recurrence_delta',
        'reader_delta','serial_delta','voice_delta',
    )

    def __post_init__(self):
        for name in self._FIELDS:
            value = tuple(getattr(self, name))
            if any(not isinstance(item, TransformationRecord) for item in value):
                raise TypeError(f'STATE_DELTA_ITEM_TYPED_REQUIRED:{name}')
            object.__setattr__(self, name, value)

    def transformations(self) -> tuple[TransformationRecord, ...]:
        return tuple(item for name in self._FIELDS for item in getattr(self, name))

    def validate(self) -> None:
        transformations=self.transformations()
        if transformations:
            if len(self.proposal_hash) != 64 or any(ch not in '0123456789abcdef' for ch in self.proposal_hash.lower()):
                raise ValueError('STATE_DELTA_PROPOSAL_BINDING_REQUIRED')
        elif self.proposal_hash and (len(self.proposal_hash) != 64 or any(ch not in '0123456789abcdef' for ch in self.proposal_hash.lower())):
            raise ValueError('STATE_DELTA_PROPOSAL_BINDING_INVALID')
        for item in transformations:
            item.validate()

    def is_empty(self) -> bool:
        return not self.transformations()


@dataclass(frozen=True)
class CheckReceipt:
    check_id: str
    check_version: str
    input_hash: str
    execution_status: str
    verdict: str
    evidence_refs: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()
    deterministic: bool = True
    confidence: float = 1.0
    dependency_receipts: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, 'evidence_refs', tuple(self.evidence_refs))
        object.__setattr__(self, 'findings', tuple(self.findings))
        object.__setattr__(self, 'dependency_receipts', tuple(self.dependency_receipts))


@dataclass(frozen=True)
class VerificationRecord:
    scene_id: str
    proposal_hash: str
    prepared_scene_hash: str
    parent_state_version: str
    parent_state_hash: str
    required_checks: tuple[str, ...]
    executed_checks: tuple[str, ...]
    check_receipts: tuple[CheckReceipt, ...]
    failures: tuple[str, ...]
    critical_unknowns: tuple[str, ...]
    qualification: QualificationStatus
    selected_card_ids: tuple[str, ...] = ()

    @property
    def evidence_ids(self) -> tuple[str, ...]:
        return tuple(ref for receipt in self.check_receipts for ref in receipt.evidence_refs)
