#!/usr/bin/env python3
"""BL VOICE ENGINE — rhythm_score.py (리듬 악보, 목소리 층 v7)

사람 원작 덩어리의 '리듬 골격'만 뽑아 악보로 쓰고, 새 장면을 그 악보 위에 쓴다.
악보에는 단어가 없다. 문단 종류(서술/대사/침묵), 문장 길이, 종결 유형, 장치(직유·욕·'!!')가 놓인 문단 위치뿐이다.

왜: 규칙(할당량)으로 리듬을 만들면 고르게 깔린다. 사람의 리듬은 고르지 않다 — 긴 서술 문단 뒤에 대사 탁구가 몰리고,
욕은 한 문단에 두 번 나왔다가 열 문단 동안 없다. 그 불균형을 지어내지 말고 진짜 사람 덩어리에서 빌린다.

  python tools/rhythm_score.py pick --preset tension [--seed 7] [--src MW,HY]   # 악보 하나 뽑아 보여 주기
  python tools/rhythm_score.py show MW-0042                                     # 특정 악보 보기
  python tools/rhythm_score.py fit 원고.md MW-0042                               # 원고가 악보를 얼마나 따랐나
  python tools/rhythm_score.py build --corpus 원작폴더                            # 악보 서고 만들기(원작 필요, numpy 불필요)

원작 코드: MW 마왕, HY 홍염의 연인, SD 세디백 첫병, CS 우리철수 (BL 원작만. 비BL·빙의글은 넣지 않는다)
"""
from __future__ import annotations
import argparse, glob, json, os, random, re, sys, unicodedata
from difflib import SequenceMatcher
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from stylofeat import normalize, split_sents, ending_class, chunk, PROF, SIMILE  # noqa: E402

LIB_PATH = os.path.join(ROOT, 'voice', 'rhythm_scores.json')
END_CODE = {'past_da': 'P', 'nonpast_da': 'N', 'colloq': 'C', 'question': 'Q', 'exclaim': 'E', 'ellipsis': 'L', 'noun_or_cut': 'X', 'other': 'X'}
END_LABEL = {'P': '과거', 'N': '현재', 'C': '구어', 'Q': '물음', 'E': '느낌', 'L': '말줄임', 'X': '명사·절단'}
WORK_CODES = {'마왕': 'MW', '홍염': 'HY', '세디': 'SD', '철수': 'CS'}
QUOTE = ('"', "'", '「', '『', '<', '[')
MIX_KEYS = ['P', 'N', 'C', 'Q', 'X']
FIT_PASS = 0.62  # 사람 덩어리가 무작위 다른 악보에 붙는 점수의 p99 위 (build 때 다시 잰다)


def skeleton(text: str) -> dict:
    paras = [p.strip() for p in normalize(text).split('\n') if p.strip() and not re.fullmatch(r'[=\-*#~ ]+', p.strip())]
    out = []
    for p in paras:
        dev = ''.join(c for c, rx in (('s', SIMILE), ('p', PROF), ('!', re.compile('!!'))) if rx.search(p))
        if re.fullmatch(r'"?…+\.?"?', p):
            out.append({'t': 'S'})
        elif p.startswith(QUOTE) or p.startswith(('-', '—', 'ㅡ')):
            ss = split_sents(p.strip('"\'「」『』'))
            out.append({'t': 'D', 'n': len(p), 'e': END_CODE[ending_class(ss[-1] if ss else p)], 'k': len(ss), 'd': dev})
        else:
            ss = split_sents(p)
            out.append({'t': 'N', 's': [[len(s), END_CODE[ending_class(s)]] for s in ss], 'd': dev})
    ends = [e for q in out if q['t'] == 'N' for _, e in q['s']]
    tot = max(1, len(ends))
    mix = {k: round(sum(1 for e in ends if e == k) / tot, 3) for k in MIX_KEYS + ['E', 'L']}
    dlg = sum(1 for q in out if q['t'] == 'D') / max(1, len(out))
    return {'chars': sum(len(p) for p in paras), 'paras': out, 'mix': mix, 'dialogue': round(dlg, 3)}


# ---------- 서고 ----------

def load_lib():
    return json.load(open(LIB_PATH, encoding='utf-8'))


def build(corpus: str, per_work: int = 150, seed: int = 1):
    from train_discriminator import read  # 인코딩 자동 판별
    r = random.Random(seed)
    lib = {'schema': 'bl_rhythm_scores.v1', 'note': '단어 없음. 문단 종류·문장 길이·종결·장치 위치만.', 'scores': {}}
    for path in sorted(glob.glob(os.path.join(corpus, '*.txt'))):
        name = unicodedata.normalize('NFC', os.path.basename(path))  # macOS·Drive 파일명은 자모가 분리(NFD)돼 올 수 있다
        code = next((c for k, c in WORK_CODES.items() if k in name), None)
        if not code:
            continue
        cs = chunk(read(path))
        cs = cs[2:-2] if len(cs) > 10 else cs
        pick = sorted(r.sample(range(len(cs)), min(per_work, len(cs))))
        for n, i in enumerate(pick):
            sk = skeleton(cs[i])
            if len(sk['paras']) < 4:
                continue
            lib['scores'][f'{code}-{n:04d}'] = sk
    # 합격선 보정: 사람 덩어리를 엉뚱한 악보에 맞춰 본 점수 분포
    ids = list(lib['scores'])
    rnd = [fit_skeletons(lib['scores'][a], lib['scores'][b])['fit'] for a, b in (r.sample(ids, 2) for _ in range(400))]
    rnd.sort()
    lib['calibration'] = {'random_pair_fit_p50': rnd[len(rnd) // 2], 'random_pair_fit_p99': rnd[int(len(rnd) * .99)],
                          'pass': round(max(FIT_PASS, rnd[int(len(rnd) * .99)] + 0.02), 3)}
    json.dump(lib, open(LIB_PATH, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    return lib


# ---------- 고르기 ----------

def preset_mix(preset: str):
    T = json.load(open(os.path.join(ROOT, 'voice', 'style_targets.json'), encoding='utf-8'))
    p = T['presets'][preset]['mix']  # past/nonpast/colloq/question/noun (%)
    return dict(zip(MIX_KEYS, [x / 100 for x in p]))


def pick(preset: str | None, seed: int | None, src: list[str] | None, lib=None):
    lib = lib or load_lib()
    items = [(k, v) for k, v in lib['scores'].items() if not src or k.split('-')[0] in src]
    if preset:
        want = preset_mix(preset)
        loud = preset in ('comedy', 'fight')

        def dist(sk):
            d = sum(abs(sk['mix'][k] - want[k]) for k in MIX_KEYS)
            bang = sum(1 for q in sk['paras'] if '!' in q.get('d', ''))
            if not loud:  # 긴장·고백·비극: '!!' 연타와 느낌표 종결이 많은 악보는 뺀다(바이블 프리셋 금지 항목)
                d += 0.5 * bang + 2 * sk['mix'].get('E', 0)
            if preset == 'tragedy':
                d += max(0, sk['dialogue'] - 0.35)
            return d
        items.sort(key=lambda kv: dist(kv[1]))
        items = items[:25]
    r = random.Random(seed)
    return r.choice(items)


def _bucket(n):
    return '짧' if n <= 12 else '중' if n <= 35 else '긴' if n <= 59 else '장'


def render(sid: str, sk: dict) -> str:
    dev_name = {'s': '직유', 'p': '욕', '!': "'!!'"}
    lines = [f"[리듬 악보 {sid}] 약 {sk['chars']}자 · 문단 {len(sk['paras'])}개 · 대사 문단 {sk['dialogue']:.0%}",
             '규칙: 내용·단어는 내 장면 것. 문단 순서와 종류는 지킨다. 문장 수는 ±1, 길이는 ±30%까지 자유. 장치 표시가 없는 문단에는 장치를 넣지 않는다.']
    for i, q in enumerate(sk['paras'], 1):
        d = q.get('d', '')
        tag = (' [' + ','.join(dev_name[c] for c in d) + ']') if d else ''
        if q['t'] == 'S':
            lines.append(f'¶{i:02d} 침묵 줄 “…….”')
        elif q['t'] == 'D':
            lines.append(f"¶{i:02d} 대사 {q['n']}자 ({q.get('k', 1)}문장, 끝 {END_LABEL[q['e']]}){tag}")
        else:
            ss = ' / '.join(f'{_bucket(n)}{n} {END_LABEL[e]}' for n, e in q['s'])
            lines.append(f"¶{i:02d} 서술 {len(q['s'])}문장: {ss}{tag}")
    return '\n'.join(lines)


# ---------- 맞춰 보기 ----------

def _seq(sk):
    return ''.join(q['t'] for q in sk['paras'])


def _ends(sk):
    return ''.join(e for q in sk['paras'] if q['t'] == 'N' for _, e in q['s'])


def _lens(sk):
    return [n for q in sk['paras'] if q['t'] == 'N' for n, _ in q['s']]


def fit_skeletons(draft: dict, score: dict) -> dict:
    a, b = _seq(draft), _seq(score)
    type_seq = SequenceMatcher(None, a, b, autojunk=False).ratio()
    count = min(len(a), len(b)) / max(1, len(a), len(b))
    ends = SequenceMatcher(None, _ends(draft), _ends(score), autojunk=False).ratio()
    # 정렬된 서술 문단끼리 문장 길이 차이
    sm = SequenceMatcher(None, a, b, autojunk=False)
    diffs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'equal':
            continue
        for x, y in zip(draft['paras'][i1:i2], score['paras'][j1:j2]):
            if x['t'] == 'N' and y['t'] == 'N':
                for (n1, _), (n2, _) in zip(x['s'], y['s']):
                    diffs.append(min(1.0, abs(n1 - n2) / max(n2, 8)))
                diffs.extend([1.0] * abs(len(x['s']) - len(y['s'])))
            elif x['t'] == 'D' and y['t'] == 'D':
                diffs.append(min(1.0, abs(x['n'] - y['n']) / max(y['n'], 8)))
    length = 1 - (sum(diffs) / len(diffs)) if diffs else 0.0
    dev_a = [q.get('d', '') != '' for q in draft['paras']]
    dev_b = [q.get('d', '') != '' for q in score['paras']]
    devices = SequenceMatcher(None, dev_a, dev_b, autojunk=False).ratio()
    fit = 0.30 * type_seq + 0.15 * count + 0.25 * ends + 0.20 * length + 0.10 * devices
    return {'fit': round(fit, 3), 'type_seq': round(type_seq, 3), 'para_count': round(count, 3), 'endings': round(ends, 3),
            'lengths': round(length, 3), 'devices': round(devices, 3)}


def fit_text(text: str, sid: str, lib=None) -> dict:
    lib = lib or load_lib()
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    r = fit_skeletons(skeleton(text), lib['scores'][sid])
    r['pass'] = r['fit'] >= lib.get('calibration', {}).get('pass', FIT_PASS)
    r['threshold'] = lib.get('calibration', {}).get('pass', FIT_PASS)
    return r


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('--corpus', required=True); b.add_argument('--per-work', type=int, default=150)
    p = sub.add_parser('pick'); p.add_argument('--preset'); p.add_argument('--seed', type=int); p.add_argument('--src')
    s = sub.add_parser('show'); s.add_argument('sid')
    f = sub.add_parser('fit'); f.add_argument('draft'); f.add_argument('sid'); f.add_argument('--json', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'build':
        lib = build(a.corpus, a.per_work)
        print(f"scores {len(lib['scores'])}  calibration {lib['calibration']}")
    elif a.cmd == 'pick':
        sid, sk = pick(a.preset, a.seed, a.src.split(',') if a.src else None)
        print(render(sid, sk))
    elif a.cmd == 'show':
        print(render(a.sid, load_lib()['scores'][a.sid]))
    else:
        r = fit_text(open(a.draft, encoding='utf-8').read(), a.sid)
        if a.json:
            print(json.dumps(r, ensure_ascii=False)); return
        print(f"=== 악보 맞춤 {a.sid}: {r['fit']} (기준 {r['threshold']}) → {'PASS' if r['pass'] else 'REWRITE'}")
        print(f"  문단 순서 {r['type_seq']} · 문단 수 {r['para_count']} · 종결 순서 {r['endings']} · 문장 길이 {r['lengths']} · 장치 위치 {r['devices']}")


if __name__ == '__main__':
    main()
