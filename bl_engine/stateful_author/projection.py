from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy




def _bounded(value, *, max_string=4000, max_items=64):
    if isinstance(value, str): return value[:max_string]
    if isinstance(value, dict): return {str(k): _bounded(v,max_string=max_string,max_items=max_items) for k,v in list(value.items())[:128]}
    if isinstance(value, (list,tuple)): return [_bounded(v,max_string=max_string,max_items=max_items) for v in list(value)[:max_items]]
    if isinstance(value, (set,frozenset)): return [_bounded(v,max_string=max_string,max_items=max_items) for v in sorted(value,key=str)[:max_items]]
    return deepcopy(value)

def _tuple(value):
    if value is None: return ()
    if isinstance(value, tuple): return value
    if isinstance(value, (list,set,frozenset)): return tuple(value)
    return (value,)


def _actor_map(narrative: dict, key: str, actor_id: str, default):
    mapping=narrative.get(key,{})
    if isinstance(mapping,dict):
        return deepcopy(mapping.get(actor_id,default))
    return deepcopy(default)


@dataclass(frozen=True)
class ActorView:
    focal_id: str
    reachable_facts: tuple[str,...]=()
    active_knowledge: tuple[str,...]=()
    active_beliefs: object=None
    relevant_memory: object=None
    relevant_unknowns: tuple[str,...]=()
    active_goals: tuple[str,...]=()
    suppressed_goal_pressure: tuple[str,...]=()
    current_body: object=None
    affective_residue: tuple[str,...]=()
    perceived_options: tuple[str,...]=()
    relationship_permissions: object=None
    attention_bias: tuple[str,...]=()
    local_judgment_policy: tuple[str,...]=()
    current_blind_spots: tuple[str,...]=()

    def to_dict(self):
        return {
            'focal_id':self.focal_id,
            'reachable_facts':list(self.reachable_facts),
            'active_knowledge':list(self.active_knowledge),
            'active_beliefs':deepcopy(self.active_beliefs or {}),
            'relevant_memory':deepcopy(self.relevant_memory or {}),
            'relevant_unknowns':list(self.relevant_unknowns),
            'active_goals':list(self.active_goals),
            'suppressed_goal_pressure':list(self.suppressed_goal_pressure),
            'current_body':deepcopy(self.current_body or {}),
            'affective_residue':list(self.affective_residue),
            'perceived_options':list(self.perceived_options),
            'relationship_permissions':deepcopy(self.relationship_permissions or {}),
            'attention_bias':list(self.attention_bias),
            'local_judgment_policy':list(self.local_judgment_policy),
            'current_blind_spots':list(self.current_blind_spots),
        }


@dataclass(frozen=True)
class RelationshipView:
    current: object
    permissions: tuple[str,...]=()
    boundaries: tuple[str,...]=()
    debts: tuple[str,...]=()

    def to_dict(self):
        return {'current':deepcopy(self.current),'permissions':list(self.permissions),'boundaries':list(self.boundaries),'debts':list(self.debts)}


@dataclass(frozen=True)
class RealizationPacket:
    scene: dict
    authority: dict
    focal_now: dict
    relationship_now: dict
    world_now: dict
    conception: dict
    cognition_artifacts: tuple[dict,...]
    realization_prior: dict
    continuity: dict

    def to_dict(self):
        return {
            'scene':deepcopy(self.scene), 'authority':deepcopy(self.authority), 'focal_now':deepcopy(self.focal_now),
            'relationship_now':deepcopy(self.relationship_now), 'world_now':deepcopy(self.world_now),
            'conception':deepcopy(self.conception), 'cognition_artifacts':[deepcopy(x) for x in self.cognition_artifacts],
            'realization_prior':deepcopy(self.realization_prior), 'continuity':deepcopy(self.continuity),
        }


def project_actor_view(actor_id: str, state: dict) -> ActorView:
    narrative=state.get('narrative_state',{}) if isinstance(state.get('narrative_state'),dict) else {}
    stored=_tuple(_actor_map(narrative,'knowledge_by_actor',actor_id,()))
    active_map=narrative.get('active_knowledge_by_actor',{}) if isinstance(narrative.get('active_knowledge_by_actor'),dict) else {}
    has_explicit_active=actor_id in active_map
    active=_tuple(active_map.get(actor_id,())) if has_explicit_active else stored
    reachable=active if has_explicit_active else stored
    beliefs=_actor_map(narrative,'beliefs_by_actor',actor_id,{})
    memory=_actor_map(narrative,'remembered_models_by_actor',actor_id,{})
    unknowns=_tuple(narrative.get('relevant_unknowns',state.get('relevant_unknowns',())))
    perceived=_tuple(_actor_map(narrative,'perceived_affordances_by_actor',actor_id,()))
    if not perceived:
        affordances=state.get('affordances',{}) if isinstance(state.get('affordances'),dict) else {}
        by_actor=affordances.get('perceived_by_actor',{})
        if isinstance(by_actor,dict): perceived=_tuple(by_actor.get(actor_id,()))
    actor_states=state.get('actor_states',{}) if isinstance(state.get('actor_states'),dict) else {}
    actor=actor_states.get(actor_id,{}) if isinstance(actor_states.get(actor_id,{}),dict) else {}
    cognition=state.get('actor_cognition',{})
    if isinstance(cognition,dict) and actor_id in cognition and isinstance(cognition[actor_id],dict):
        actor={**actor,**cognition[actor_id]}
    voice=state.get('voice_state',{}) if isinstance(state.get('voice_state'),dict) else {}
    rel=project_relationship_view(actor_id,state)
    return ActorView(
        focal_id=actor_id, reachable_facts=reachable, active_knowledge=active,
        active_beliefs=beliefs, relevant_memory=memory, relevant_unknowns=unknowns,
        active_goals=_tuple(actor.get('active_goals',())), suppressed_goal_pressure=_tuple(actor.get('suppressed_goals',())),
        current_body=deepcopy(actor.get('body_state',{})), affective_residue=_tuple(actor.get('affective_residue',())),
        perceived_options=perceived, relationship_permissions=rel.to_dict(),
        attention_bias=_tuple(voice.get('attention_habits',actor.get('attention_bias',()))),
        local_judgment_policy=_tuple(voice.get('judgment_logic',actor.get('local_judgment_policy',()))),
        current_blind_spots=_tuple(actor.get('blind_spots',())),
    )


def project_relationship_view(actor_id: str, state: dict) -> RelationshipView:
    rel=state.get('relationship_state',{})
    if not isinstance(rel,dict): return RelationshipView({})
    # Prefer actor-scoped/pair-scoped records. A flat relationship state is treated as the already-relevant current edge.
    current=rel.get(actor_id,rel)
    if not isinstance(current,dict): current={'state':current}
    return RelationshipView(
        current={k:deepcopy(v) for k,v in current.items() if k not in {'hidden_plan','omniscient_truth'}},
        permissions=_tuple(current.get('permissions',())), boundaries=_tuple(current.get('boundaries',())), debts=_tuple(current.get('debts',())),
    )


def _visible_world(state: dict) -> dict:
    event=state.get('event',{}) if isinstance(state.get('event'),dict) else {}
    allowed={'visible_action','visible_environment','location','time','objects','current_constraints'}
    return {k:_bounded(v) for k,v in event.items() if k in allowed or k.startswith('visible_')}


def _realization_prior(state: dict) -> dict:
    voice=state.get('voice_state',{}) if isinstance(state.get('voice_state'),dict) else {}
    allowed={'attention_habits','judgment_logic','emotional_evasion','reality_anchors','abstraction_band','lyric_return_path'}
    return {k:deepcopy(v) for k,v in voice.items() if k in allowed}


def build_realization_packet(contract, state:dict, cognition_artifacts=(), *, conception:dict|None=None) -> RealizationPacket:
    focal=project_actor_view(contract.focal_character_id,state)
    rel=project_relationship_view(contract.focal_character_id,state)
    return RealizationPacket(
        scene={'scene_id':contract.scene_id,'focal_id':contract.focal_character_id,'narrator_mode':contract.narrator_mode,'requested_action':contract.requested_action},
        authority={'required_events':list(contract.required_events),'prohibited_events':list(contract.active_prohibitions),'locked_canon_refs':list(contract.locked_canon_refs),'creative_freedom':contract.creative_freedom},
        focal_now=focal.to_dict(), relationship_now=rel.to_dict(), world_now=_visible_world(state),
        conception=deepcopy(conception or {}), cognition_artifacts=tuple(deepcopy(tuple(cognition_artifacts))),
        realization_prior=_realization_prior(state), continuity={},
    )


def _flatten_sensitive_strings(value):
    if isinstance(value,str):
        if len(value.strip()) >= 4:
            yield value.strip()
        return
    if isinstance(value,dict):
        for v in value.values():
            yield from _flatten_sensitive_strings(v)
        return
    if isinstance(value,(list,tuple,set,frozenset)):
        for v in value:
            yield from _flatten_sensitive_strings(v)


def collect_unreachable_literals(actor_id: str, state: dict) -> tuple[str,...]:
    """Planner/verifier-only exact-string guard. Never enters the writer packet."""
    narrative=state.get('narrative_state',{}) if isinstance(state.get('narrative_state'),dict) else {}
    focal=project_actor_view(actor_id,state)
    reachable=set(map(str,(*focal.reachable_facts,*focal.active_knowledge,*focal.perceived_options)))
    candidates=[]
    knowledge=narrative.get('knowledge_by_actor',{}) if isinstance(narrative.get('knowledge_by_actor'),dict) else {}
    for other_id, values in knowledge.items():
        if other_id == actor_id: continue
        candidates.extend(_flatten_sensitive_strings(values))
    for key in ('hidden_master_plan','omniscient_truth','objective_truth','correct_answer'):
        if key in narrative: candidates.extend(_flatten_sensitive_strings(narrative[key]))
        if key in state: candidates.extend(_flatten_sensitive_strings(state[key]))
    for value in (narrative.get('objective_affordances',()),):
        candidates.extend(_flatten_sensitive_strings(value))
    affordances=state.get('affordances',{}) if isinstance(state.get('affordances'),dict) else {}
    candidates.extend(_flatten_sensitive_strings(affordances.get('objective',())))
    reader=state.get('reader_model',{})
    if isinstance(reader,dict):
        for key in ('correct_answer','hidden_reader_target','omniscient_answer'):
            if key in reader: candidates.extend(_flatten_sensitive_strings(reader[key]))
    out=[]
    for token in candidates:
        if token in reachable: continue
        if token not in out: out.append(token)
    return tuple(out)
