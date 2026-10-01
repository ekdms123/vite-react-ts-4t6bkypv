from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum


class InformationNeed(str, Enum):
    CURIOSITY = 'CURIOSITY'
    SUSPENSE = 'SUSPENSE'
    SURPRISE = 'SURPRISE'


class HypothesisStatus(str, Enum):
    DOMINANT='DOMINANT'
    PLAUSIBLE='PLAUSIBLE'
    WEAK='WEAK'
    LATENT='LATENT'
    DISCONFIRMED='DISCONFIRMED'


@dataclass(frozen=True)
class ReaderHypothesis:
    hypothesis_id: str
    model: str
    evidence_refs: tuple[str, ...] = ()
    confidence_band: str = 'UNKNOWN'
    active: bool = True
    status: HypothesisStatus | None = None

    def __post_init__(self):
        object.__setattr__(self, 'evidence_refs', tuple(self.evidence_refs))
        if self.confidence_band not in {'LOW','MEDIUM','HIGH','UNKNOWN'}:
            raise ValueError('READER_CONFIDENCE_BAND_INVALID')
        if self.status is None:
            derived=HypothesisStatus.LATENT if not self.active else (
                HypothesisStatus.DOMINANT if self.confidence_band=='HIGH' else
                HypothesisStatus.PLAUSIBLE if self.confidence_band in {'MEDIUM','UNKNOWN'} else HypothesisStatus.WEAK
            )
            object.__setattr__(self,'status',derived)


@dataclass(frozen=True)
class ReaderModel:
    hypotheses: tuple[ReaderHypothesis, ...] = ()
    active_questions: tuple[str, ...] = ()
    retrievable_evidence: tuple[str, ...] = ()
    suppressed_evidence: tuple[str, ...] = ()
    tractability: str = 'MEDIUM'
    engagement_route: str | None = None

    def __post_init__(self):
        object.__setattr__(self, 'hypotheses', tuple(self.hypotheses))
        object.__setattr__(self, 'active_questions', tuple(self.active_questions))
        object.__setattr__(self, 'retrievable_evidence', tuple(self.retrievable_evidence))
        object.__setattr__(self, 'suppressed_evidence', tuple(self.suppressed_evidence))
        if self.tractability not in {'LOW','MEDIUM','HIGH','UNKNOWN'}:
            raise ValueError('READER_TRACTABILITY_INVALID')

    def active_hypotheses(self) -> tuple[ReaderHypothesis, ...]:
        return tuple(h for h in self.hypotheses if h.active and h.status is not HypothesisStatus.DISCONFIRMED)


@dataclass(frozen=True)
class ReaderView:
    active_hypotheses: tuple[ReaderHypothesis,...]=()
    active_questions: tuple[str,...]=()
    active_evidence: tuple[str,...]=()
    stale_evidence: tuple[str,...]=()
    tractability: str='MEDIUM'
    engagement_route: str | None=None
    retrieval_cues: tuple[tuple[str,str],...]=()


@dataclass(frozen=True)
class EvidenceGainResult:
    progress: bool
    answer_gain: bool
    changed_hypotheses: tuple[str,...]=()


def build_reader_view(model: ReaderModel | None) -> ReaderView:
    model=model or ReaderModel()
    return ReaderView(model.active_hypotheses(),tuple(model.active_questions),tuple(model.retrievable_evidence),
                      tuple(model.suppressed_evidence),model.tractability,model.engagement_route,())


def reactivate_evidence(view: ReaderView, evidence_id: str, cue_ref: str) -> ReaderView:
    if evidence_id not in view.stale_evidence:
        return view
    active=tuple(dict.fromkeys((*view.active_evidence,evidence_id)))
    stale=tuple(x for x in view.stale_evidence if x!=evidence_id)
    cues=tuple((*view.retrieval_cues,(evidence_id,cue_ref)))
    return replace(view,active_evidence=active,stale_evidence=stale,retrieval_cues=cues)


def evidence_gain_without_answer_gain(before: dict, after: dict, *, answer_revealed: bool) -> EvidenceGainResult:
    keys=set(before)|set(after)
    changed=tuple(sorted(k for k in keys if before.get(k)!=after.get(k)))
    return EvidenceGainResult(bool(changed),bool(answer_revealed),changed)
