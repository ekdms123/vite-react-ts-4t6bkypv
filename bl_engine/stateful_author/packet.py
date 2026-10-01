from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json
import jsonschema
from .intelligence import AuthorizedIntelligencePayload
from .projection import build_realization_packet

_ALLOWED_TOP = {
    'event','voice_state','narrative_state','serial_pressure','cognition_artifacts','surface_contract',
    'relevant_recurrences','open_loops','author_intelligence','relationship_state','relevant_unknowns',
    'previous_verified_delta','actor_cognition','reader_model','affordances',
}
_FORBIDDEN_GENERAL_KEYS = {
    'closure_target','author_analysis','source_author','source_text','source_excerpt','verification',
    'failure_codes','failure_history','full_history','commercial_ledger','unused_world_state',
    'verifier_commentary',
}
_MAX_LIST=64
_MAX_STRING=4000


def _clean(value, *, path=()):
    if isinstance(value, dict):
        out={}
        for i,(k,v) in enumerate(value.items()):
            if i >= 128: break
            if k in _FORBIDDEN_GENERAL_KEYS: continue
            out[k]=_clean(v,path=path+(k,))
        return out
    if isinstance(value, (list,tuple)):
        return [_clean(v,path=path) for v in value[:_MAX_LIST]]
    if isinstance(value, (set,frozenset)):
        return [_clean(v,path=path) for v in sorted(value,key=str)[:_MAX_LIST]]
    if isinstance(value,str): return value[:_MAX_STRING]
    return deepcopy(value)


def _clean_author_intelligence(value)->list[dict]:
    if not isinstance(value,list): return []
    cleaned=[]
    for item in value[:8]:
        if not isinstance(item,dict): continue
        card_id=item.get('id'); guidance=item.get('guidance')
        if not isinstance(card_id,str) or not card_id or not isinstance(guidance,list): continue
        lines=[str(x)[:_MAX_STRING] for x in guidance if isinstance(x,str) and x.strip()][:4]
        if lines: cleaned.append({'id':card_id,'guidance':lines})
    return cleaned


def compile_writer_packet(state:dict)->dict:
    """Legacy compatibility adapter only. Official runtime uses build_writer_packet/projector."""
    packet={}
    for key,value in state.items():
        if key not in _ALLOWED_TOP: continue
        packet[key]=_clean_author_intelligence(value) if key=='author_intelligence' else _clean(value,path=(key,))
    return packet


def _validate_contract(contract):
    required=('scene_id','focal_character_id','requested_action','required_events','active_prohibitions','locked_canon_refs','creative_freedom','parent_state_version','narrator_mode')
    if contract is None or any(not hasattr(contract,k) for k in required): raise ValueError('SCENE_CONTRACT_REQUIRED')
    if not contract.scene_id or not contract.focal_character_id or not contract.requested_action: raise ValueError('SCENE_CONTRACT_INVALID')


def _specialist_artifacts(authorized_payloads, library):
    allowed_artifact_keys={
        'relationship_state','voice_state.attention_habits','voice_state.judgment_logic','relevant_recurrences',
        'narrative_state.present_consequence','permission','current_constraints',
    }
    out=[]
    for item in authorized_payloads:
        if not isinstance(item,AuthorizedIntelligencePayload): raise ValueError('FORGED_INTELLIGENCE:payload_not_compiled')
        card=library.get(item.id)
        if card is None or card.version != item.version: raise ValueError(f'FORGED_INTELLIGENCE:{item.id}')
        artifact={k:_clean(v) for k,v in item.artifact if k in allowed_artifact_keys}
        if artifact:
            out.append({'specialist_id':item.id,'version':item.version,'artifact':artifact})
    return out


def build_writer_packet(contract,state:dict,authorized_payloads,library,*,conception:dict|None=None)->dict:
    _validate_contract(contract)
    artifacts=_specialist_artifacts(authorized_payloads,library)
    packet=build_realization_packet(contract,state,artifacts,conception=conception).to_dict()
    schema_path=Path(__file__).resolve().parents[1] / 'runtime' / 'WRITER_PACKET_SCHEMA.json'
    schema=json.loads(schema_path.read_text(encoding='utf-8'))
    try: jsonschema.validate(packet,schema)
    except jsonschema.ValidationError as exc: raise ValueError(f'WRITER_PACKET_SCHEMA_INVALID:{exc.message}') from exc
    return packet
