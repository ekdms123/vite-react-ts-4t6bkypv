from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from .epistemic import freeze


@dataclass(frozen=True)
class SceneReceipt:
    scene_id: str
    qualification_status: str
    parent_state_version: str | None
    candidate_delta: object
    committed_delta: object
    voice_candidate_delta: object
    intelligence_cards_used: tuple[str,...]=()
    intelligence_effects_verified: tuple[str,...]=()
    intelligence_effects_rejected: tuple[str,...]=()
    verification_evidence_ids: tuple[str,...]=()
    resulting_state_version: str | None=None
    parent_state_hash: str | None=None
    resulting_state_hash: str | None=None
    proposal_hash: str | None=None
    prepared_scene_hash: str | None=None

    @property
    def verified(self)->bool:
        return self.qualification_status == 'PASS'

    @property
    def state_delta(self):
        return self.committed_delta


def make_scene_receipt(*,scene_id:str,verified:bool,state_delta:dict,proposed_voice_delta:dict,
                       intelligence_cards_used=(),intelligence_effects_verified=(),intelligence_effects_rejected=(),
                       parent_state_version=None,verification_evidence_ids=(),resulting_state_version=None,
                       parent_state_hash=None,resulting_state_hash=None,proposal_hash=None,prepared_scene_hash=None)->SceneReceipt:
    used=tuple(intelligence_cards_used)
    verified_effects=tuple(intelligence_effects_verified) if verified else ()
    if any(effect not in set(used) for effect in verified_effects):
        raise ValueError('RECEIPT_EFFECT_NOT_USED')
    candidate=freeze(state_delta)
    committed=freeze(state_delta if verified else {})
    voice=freeze(proposed_voice_delta if verified else {})
    return SceneReceipt(
        scene_id=scene_id,
        qualification_status='PASS' if verified else 'FAIL',
        parent_state_version=parent_state_version,
        candidate_delta=candidate,
        committed_delta=committed,
        voice_candidate_delta=voice,
        intelligence_cards_used=used,
        intelligence_effects_verified=verified_effects,
        intelligence_effects_rejected=tuple(intelligence_effects_rejected),
        verification_evidence_ids=tuple(verification_evidence_ids),
        resulting_state_version=resulting_state_version,
        parent_state_hash=parent_state_hash,
        resulting_state_hash=resulting_state_hash,
        proposal_hash=proposal_hash,
        prepared_scene_hash=prepared_scene_hash,
    )
