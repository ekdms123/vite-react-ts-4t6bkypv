#!/usr/bin/env python3
"""BL VOICE ENGINE — slop_forensics_ko.py

AI 글이 사람 BL 원작보다 '과하게' 쓰는 어절·2어절을 데이터로 찾는다. banlist 후보를 만드는 도구.
알고리즘은 sam-paech/slop-forensics(MIT, vendor/slop-forensics)의 find_over_represented_words를 그대로 옮겼고,
토큰화만 한국어 어절로 바꿨다(원본은 [a-zA-Z']+만 세서 한국어를 0개로 본다).

  python tools/slop_forensics_ko.py --ai AI폴더 --human 원작폴더 [--n 1] [--top 40] [--min-files 3]

- 같은 AI 파일 하나에서만 나온 단어(소재 단어)는 --min-files로 거른다.
- 결과는 '후보'다. 소재 단어(교복·의자 같은)는 손으로 빼고, 남은 문체 단어만 banlist에 올린다.
- 사람 원작 쪽 단어 목록은 출력하지 않는다(원작 어휘 유출 방지). 비율만 쓴다.
"""
from __future__ import annotations
import argparse, glob, os, re, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from stylofeat import normalize  # noqa: E402


# --- vendor/slop-forensics/analysis_upstream.py 에서 옮김 (MIT, Copyright (c) 2025 Sam Paech) ---
def find_over_represented_words(corpus_frequencies, wordfreq_frequencies, top_n=50000):
    over_representation = {}
    epsilon = 1e-12
    for word, corpus_freq in corpus_frequencies.items():
        wordfreq_freq = wordfreq_frequencies.get(word, 0)
        ratio = corpus_freq / max(wordfreq_freq, epsilon)
        over_representation[word] = (ratio, corpus_freq, wordfreq_freq)
    sorted_words = sorted(over_representation.items(), key=lambda item: item[1][0], reverse=True)
    return [(word, data[0], data[1], data[2]) for word, data in sorted_words[:top_n]]
# --- 옮긴 부분 끝 ---


def read(p):
    b = open(p, 'rb').read()
    for enc in ('utf-8', 'cp949', 'utf-16'):
        try:
            t = b.decode(enc)
            break
        except UnicodeDecodeError:
            t = None
    if t is None:
        t = b.decode('utf-8', 'ignore')
    return re.sub(r'<!--.*?-->', '', t, flags=re.S)  # 샘플 머리 주석은 본문이 아니다


def toks(t):
    out = []
    for w in normalize(t).split():
        w = re.sub(r'[^가-힣]', '', w)
        if len(w) >= 2:
            out.append(w)
    return out


def grams(ts, n):
    return [' '.join(ts[i:i + n]) for i in range(len(ts) - n + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ai', required=True)
    ap.add_argument('--human', required=True)
    ap.add_argument('--n', type=int, default=1)
    ap.add_argument('--top', type=int, default=40)
    ap.add_argument('--min-files', type=int, default=3)
    a = ap.parse_args()
    hc = Counter()
    for p in glob.glob(os.path.join(a.human, '*.txt')):
        hc.update(grams(toks(read(p)), a.n))
    N = max(1, sum(hc.values()))
    ac, files = Counter(), {}
    for p in glob.glob(os.path.join(a.ai, '*.txt')) + glob.glob(os.path.join(a.ai, '*.md')):
        for g in grams(toks(read(p)), a.n):
            ac[g] += 1
            files.setdefault(g, set()).add(p)
    M = max(1, sum(ac.values()))
    af = {w: c / M for w, c in ac.items() if c >= 3 and len(files[w]) >= a.min_files}
    hf = {w: (hc.get(w, 0) + 0.5) / N for w in af}
    print(f'# AI {M}어절 / 원작 {N}어절. ratio = AI 빈도 ÷ 원작 빈도. 소재 단어는 손으로 뺀다.')
    print('gram\tratio\tai_per_10k\thuman_per_10k\tai_files')
    for w, r, x, y in find_over_represented_words(af, hf, a.top):
        print(f'{w}\t{r:.1f}\t{x * 1e4:.2f}\t{y * 1e4:.2f}\t{len(files[w])}')


if __name__ == '__main__':
    main()
