from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class UptakeEvidence:
    generated_action: str
    observed_uptake: str
    proposed_frame: str
    evidence_refs: tuple[str,...]=()
    def __post_init__(self):
        object.__setattr__(self,'evidence_refs',tuple(self.evidence_refs))


@dataclass(frozen=True)
class InteractionFrameConfirmation:
    prior_frame: str
    new_frame: str
    confirmed: bool
    evidence_refs: tuple[str,...]=()
    reason: str=''


def confirm_interaction_frame(prior_frame: str, uptake: UptakeEvidence) -> InteractionFrameConfirmation:
    grounded=bool(uptake.generated_action.strip() and uptake.observed_uptake.strip() and uptake.proposed_frame.strip() and uptake.evidence_refs)
    if not grounded:
        return InteractionFrameConfirmation(prior_frame,prior_frame,False,tuple(uptake.evidence_refs),'INSUFFICIENT_UPTAKE_EVIDENCE')
    return InteractionFrameConfirmation(prior_frame,uptake.proposed_frame,True,tuple(uptake.evidence_refs),'POST_GENERATION_UPTAKE_CONFIRMED')
