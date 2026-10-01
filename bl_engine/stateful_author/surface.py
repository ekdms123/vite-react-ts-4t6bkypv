from __future__ import annotations
from dataclasses import dataclass
import re

_DIALOGUE_PREFIXES = ('"', '“', '‘', "'", '-', '—')
_SECTION_RE = re.compile(r'^(?:\d+[월장]|[-*@]+|[A-Z][A-Z _-]{2,})$')
_SENT_RE = re.compile(r'[.!?…。！？]+(?:["”’\']*)')


@dataclass(frozen=True)
class ProseBlock:
    index: int
    text: str
    sentence_count: int
    dialogue: bool
    section_boundary: bool
    source_line: int


def _is_dialogue(text: str) -> bool:
    s=text.strip()
    return bool(s) and s.startswith(_DIALOGUE_PREFIXES)


def _is_section_boundary(text: str) -> bool:
    s=text.strip()
    return not s or bool(_SECTION_RE.match(s))


def _sentence_count(text: str) -> int:
    s=text.strip()
    if not s: return 0
    hits=len(_SENT_RE.findall(s))
    return hits if hits else 1


def parse_prose(text: str) -> tuple[ProseBlock, ...]:
    """Parse physical prose blocks. In plain-text fiction, a non-empty newline is treated as a paragraph boundary.
    Blank lines remain represented by the line positions, not as prose blocks.
    """
    blocks=[]
    for line_no,line in enumerate(text.splitlines() or [text], start=1):
        s=line.strip()
        if not s: continue
        blocks.append(ProseBlock(len(blocks),s,_sentence_count(s),_is_dialogue(s),_is_section_boundary(s),line_no))
    return tuple(blocks)


def evaluate_paragraph_topology(text: str, context: dict | None = None) -> list[str]:
    context=context or {}
    blocks=parse_prose(text)
    authorized=set(context.get('authorized_isolation_texts',()))
    narrative=[b for b in blocks if not b.dialogue and not b.section_boundary]
    effective=[b for b in narrative if b.text not in authorized]
    failures=[]
    if len(effective) >= 3:
        counts=[b.sentence_count for b in effective]
        # Consecutive narrative one-beat blocks, regardless of character length or punctuation presence.
        run=0
        for count in counts:
            run=run+1 if count==1 else 0
            if run>=3:
                failures.append('PARAGRAPH_FRAGMENTATION'); break
        # Rolling staircase such as 1/2/1/2/1: many isolated beats with no substantial paragraph.
        if 'PARAGRAPH_FRAGMENTATION' not in failures:
            for i in range(max(1,len(counts)-4)):
                w=counts[i:i+5]
                if len(w)>=5 and sum(c==1 for c in w)>=3 and all(c<=2 for c in w):
                    failures.append('PARAGRAPH_FRAGMENTATION'); break
    if len(narrative)>=4:
        counts=[b.sentence_count for b in narrative]
        if len(set(counts))==1 and counts[0]>=2:
            failures.append('PARAGRAPH_REGULARIZATION')
    return list(dict.fromkeys(failures))
