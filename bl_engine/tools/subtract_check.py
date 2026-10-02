#!/usr/bin/env python3
"""BL VOICE ENGINE — subtract_check.py (빼기만 했는가)

말로 쏟아 낸 초고(raw)에서 '빼기만' 해서 완성본(final)을 만들었는지 검사한다.
완성본의 어절이 초고에 같은 순서로 있으면 '남긴 말', 없으면 '더한 말'이다.

  python tools/subtract_check.py 초고.md 완성.md            # 리포트
  python tools/subtract_check.py 초고.md 완성.md --json

왜: 다듬으면서 더한 말이 '잘 쓰려고 노력한 느낌'의 출처다. 교훈 한 줄, 마무리 농담, 비유, 앞뒤를 맞춘 회수 문장은
거의 언제나 퇴고 때 '더해진' 것이다. 이 도구는 퇴고를 빼기·순서 바꾸기·조사/어미 손질로만 제한한다.

- 조사·어미가 바뀐 것(갔다→갔음, 청첩장이→청첩장)은 남긴 말로 친다(앞부분이 같으면 같은 말).
- 해시태그 줄, '제목:'으로 시작하는 줄, HTML 주석은 검사하지 않는다(제목은 --title로 따로 검사).
- 통과: 더한 어절이 전체의 8% 이하이고, 덧칠 단어(결국·마치·문득·비로소…)를 새로 더하지 않았을 것.
"""
from __future__ import annotations
import json, re, sys

POLISH = ('결국', '마치', '문득', '비로소', '어쩌면', '그제야', '왠지', '이상하게', '묘하게', '가만히', '조용히', '천천히',
          '처럼', '듯', '같았다', '것이다', '법이다', '마련이다', '순간', '여전히', '그렇게', '그래서인지')
MAX_ADDED = 0.08


def _clean(text: str) -> str:
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    keep = []
    for ln in text.split('\n'):
        s = ln.strip()
        if not s or s.startswith('제목:') or re.fullmatch(r'(#\S+\s*)+', s) or re.fullmatch(r'[=\-*_ ]+', s):
            continue
        keep.append(re.sub(r'^#+\s*', '', s))  # 마크다운 소제목 기호만 떼고 말은 검사한다
    return '\n'.join(keep)


def tokens(text: str):
    out = []
    for w in _clean(text).split():
        t = re.sub(r'[^가-힣A-Za-z0-9]', '', w)
        if t:
            out.append(t)
    return out


def same(a: str, b: str) -> bool:
    if a == b:
        return True
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n >= 1 and n >= min(len(a), len(b)) - 1 and (min(len(a), len(b)) >= 2 or n == min(len(a), len(b)))


def align(raw, fin):
    """LCS(같은 순서로 남은 말). 반환: final 각 어절이 초고에서 왔는지 여부."""
    n, m = len(raw), len(fin)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        ri = raw[i]; row = dp[i]; nxt = dp[i + 1]
        for j in range(m - 1, -1, -1):
            row[j] = nxt[j + 1] + 1 if same(ri, fin[j]) else max(nxt[j], row[j + 1])
    kept = [False] * m
    i = j = 0
    while i < n and j < m:
        if same(raw[i], fin[j]) and dp[i][j] == dp[i + 1][j + 1] + 1:
            kept[j] = True; i += 1; j += 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            i += 1
        else:
            j += 1
    return kept


def check(raw_text: str, final_text: str, max_added: float = MAX_ADDED) -> dict:
    raw, fin = tokens(raw_text), tokens(final_text)
    kept = align(raw, fin)
    added = [(k, w) for k, (w, ok) in enumerate(zip(fin, kept)) if not ok]
    ratio = len(added) / max(1, len(fin))
    raw_join = ' '.join(raw)
    polish = sorted({p for _, w in added for p in POLISH if p in w and p not in raw_join})
    spans, cur = [], []
    for k, w in added:
        if cur and k != cur[-1][0] + 1:
            spans.append(' '.join(x for _, x in cur)); cur = []
        cur.append((k, w))
    if cur:
        spans.append(' '.join(x for _, x in cur))
    return {
        'raw_words': len(raw), 'final_words': len(fin), 'kept_ratio_of_raw': round(sum(kept) / max(1, len(raw)), 3),
        'added_words': len(added), 'added_ratio': round(ratio, 3), 'added_spans': spans, 'polish_added': polish,
        'verdict': 'PASS' if ratio <= max_added and not polish else 'REWRITE',
    }


def check_title(raw_text: str, title: str, keywords=('매일', '글쓰기', '챌린지', '일차', '1일차', '2일차', '3일차', '글감', '10월')) -> list:
    """제목은 초고에 있던 말로 만든다. 검색 키워드는 예외."""
    raw = tokens(raw_text)
    out = []
    for w in tokens(title):
        if any(k in w for k in keywords):
            continue
        if not any(same(w, r) for r in raw):
            out.append(w)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 2:
        print(__doc__); sys.exit(1)
    raw_text = open(args[0], encoding='utf-8').read()
    final_text = open(args[1], encoding='utf-8').read()
    r = check(raw_text, final_text)
    t = re.search(r'^제목:\s*(.+)$', final_text, re.M)
    r['title_new_words'] = check_title(raw_text, t.group(1)) if t else None
    if '--json' in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=1)); return
    print(f"=== 빼기 검사  → {r['verdict']}")
    print(f"초고 {r['raw_words']}어절 → 완성 {r['final_words']}어절 (초고의 {r['kept_ratio_of_raw']:.0%}를 남김)")
    print(f"더한 말 {r['added_words']}어절 ({r['added_ratio']:.1%}, 기준 {MAX_ADDED:.0%} 이하)")
    for s in r['added_spans'][:15]:
        print(f'  [더함] {s}')
    if r['polish_added']:
        print(f"  [덧칠] 초고에 없던 다듬는 말을 더함: {', '.join(r['polish_added'])} → 지운다")
    if r['title_new_words']:
        print(f"  [제목] 초고에 없던 말: {', '.join(r['title_new_words'])} → 초고 속 말로 바꾼다(검색 키워드는 예외)")


if __name__ == '__main__':
    main()
