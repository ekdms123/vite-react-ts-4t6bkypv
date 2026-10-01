from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class RepairPacket:
    original_packet_ref: str
    failing_spans: tuple[str,...]
    root_depth: str
    failure_family: str
    allowed_changes: tuple[str,...]
    protected_spans: tuple[str,...]=()
    protected_events: tuple[str,...]=()
    required_effect: str=''


_INVALIDATION={
    'PARAGRAPH_TOPOLOGY': {'WORDING','PARAGRAPH_STRUCTURE'},
    'MODEL_PRIOR': {'WORDING','PARAGRAPH_STRUCTURE','DISCOURSE_STRUCTURE'},
    'KNOWLEDGE_REACHABILITY': {'EVENT_ORDER','FACT_CONTENT','KNOWLEDGE_CONTENT'},
    'HARD_USER_BANS': {'WORDING'},
}


def invalidate_check_receipts(receipts, changed_dimensions:set[str]|frozenset[str]):
    changed=set(changed_dimensions)
    return tuple(r for r in receipts if not (_INVALIDATION.get(r.check_id,set()) & changed))


def failure_root_depth(code:str, repeat_count:int=1)->str:
    if repeat_count>=3 and code in {'PARAGRAPH_FRAGMENTATION','PARAGRAPH_REGULARIZATION','TERMINAL_CLOSURE_STACK'}:
        return 'COGNITION'
    if repeat_count>=2 and code in {'PARAGRAPH_FRAGMENTATION','PARAGRAPH_REGULARIZATION','TERMINAL_CLOSURE_STACK','FORMULAIC_RHETORIC'}:
        return 'DISCOURSE'
    if code.startswith('LEXICAL_'): return 'LEXICON'
    if code in {'PARAGRAPH_FRAGMENTATION','PARAGRAPH_REGULARIZATION','UNSUPPORTED_ISOLATION'}: return 'PARAGRAPH'
    if code in {'FORMULAIC_RHETORIC','SEMANTIC_ECHO','ABSTRACT_RESTATEMENT','TERMINAL_CLOSURE_STACK'}: return 'DISCOURSE'
    if code in {'AFFECTIVE_NORMALIZATION','SELF_MODEL_OVERRESOLUTION','CHARACTER_GENERICITY'}: return 'COGNITION'
    if code in {'KNOWLEDGE_LEAK','CANON_VIOLATION'}: return 'AUTHORITY'
    return 'CONCEPTION'
