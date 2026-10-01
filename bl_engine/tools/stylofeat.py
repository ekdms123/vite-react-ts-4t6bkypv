#!/usr/bin/env python3
"""BL VOICE ENGINE — stylofeat.py

판별기(discriminator.py)가 쓰는 추상 문체 특징. 표준 라이브러리만 쓴다.

원칙
- 원작의 단어·문장은 특징으로 쓰지 않는다. 문법 꼬리(조사·어미), 문장부호, 길이·리듬, 장치의 '분포'만 잰다.
- 표기 차이(“ ” vs " ", ... vs …, 줄머리 - 대사)는 먼저 정규화한다. 2010년대 연재 표기 습관이 아니라 언어 습관을 재기 위해서다.
- 형태소 분석기(kiwipiepy)에 의존하지 않는다. 같은 글은 어느 환경에서도 같은 값을 낸다.
"""
from __future__ import annotations
import re, math, statistics as st, unicodedata

# 조사·어미 꼬리 후보(문법 형태만. 내용어는 넣지 않는다)
TAILS = [
    '은', '는', '이', '가', '을', '를', '에', '에서', '에게', '한테', '께', '로', '으로', '와', '과', '랑', '이랑', '하고',
    '도', '만', '까지', '부터', '조차', '마저', '밖에', '보다', '처럼', '같이', '의', '요', '죠', '지', '네', '군', '데',
    '고', '며', '면', '서', '니', '니까', '는데', '지만', '거든', '잖아', '래', '대', '냐', '나', '까', '야', '아', '어',
    '다', '었다', '았다', '였다', '했다', '한다', '는다', '이다', '였', '던', '는', '은', '을', '게', '도록', '듯', '채',
    '자', '자마자', '면서', '다가', '려고', '러', '든', '든지', '거나', '라', '라고', '다고', '냐고', '자고', '래서',
]
TAILS = sorted(set(TAILS), key=lambda x: (-len(x), x))

PROF = re.compile(r'(시발|씨발|씨팔|존나|좆|새끼|병신|지랄|썅|개같|염병|빌어먹|젠장|제기랄|니미)')
SIMILE = re.compile(r'(처럼|듯이|듯한|마치|인 양|같았다)')
CONJ = re.compile(r'^(그리고|하지만|그러나|그래서|그런데|그러자|그러니까|그러면|게다가|또한|결국|마침내|그제야|그때)\b')
NUM_HANGUL = re.compile(r'(?<![가-힣])(한|두|세|네|다섯|여섯|일곱|여덟|아홉|열|스물|서른|마흔|쉰|일|이|삼|사|오|육|칠|팔|구|십|백|천|만)+ ?(시|분|초|년|개|명|번|살|시간|페이지|층|대|원|잔|장|권|걸음|도시|퍼센트)(?![가-힣])')
PRON_GEU = re.compile(r'(?<![가-힣])그(가|는|의|를|에게|와|도)(?= )')
SENSE_VERB = re.compile(r'(느껴졌다|느꼈다|깨달았다|알 수 있었다|알 수 없었다|생각했다|떠올렸다)')
NEG_DA = re.compile(r'지 않았다')
HEDGE = re.compile(r'(조금|아주|살짝|미세하게|천천히|이상하게|묘하게|생각보다)')
EYE = re.compile(r'(시선|눈동자|눈빛|눈이 마주|고개를 (끄덕|숙|들|돌))')


def normalize(text: str) -> str:
    t = unicodedata.normalize('NFC', text).replace('\r', '')
    t = t.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    t = re.sub(r'\.{3,}', '…', t)
    t = re.sub(r'…+', '…', t)
    t = re.sub(r'[ \t]+', ' ', t)
    lines = []
    for ln in t.split('\n'):
        s = ln.strip()
        # 줄머리 대사 표기(-말, ㅡ말, —말)를 따옴표 대사로 통일
        m = re.match(r'^[-ㅡ—–]\s*(.+)$', s)
        if m and not s.startswith('---'):
            s = '"' + m.group(1).strip() + '"'
        lines.append(s)
    return '\n'.join(lines)


def split_sents(p: str):
    return [s.strip() for s in re.split(r'(?<=[.!?…])\s+', p) if s.strip()]


def ending_class(s: str) -> str:
    t = s.rstrip('"\' ')
    if t.endswith('…'):
        return 'ellipsis'
    if t.endswith('?'):
        return 'question'
    if t.endswith('!'):
        return 'exclaim'
    t = t.rstrip('.!?… ')
    if not t:
        return 'other'
    if re.search(r'(었|았|였|했|웠|겼|렸|졌|됐|갔|왔|섰|쳤|켰|냈|뤘|녔|셨|혔|꼈|뒀|봤|줬|팠|랐|났|샀|잤|탔|썼|컸|껐|쪘|펐)다$', t):
        return 'past_da'
    if t.endswith('다'):
        return 'nonpast_da'
    if re.search(r'(지|네|군|나|까|야|아|어|래|걸|데|게|고|며|면서|서|니|구나|소|오|구려|느냐|거라|니라|세|잖아|거든|요|죠)$', t):
        return 'colloq'
    return 'noun_or_cut'


def _vmr(counts):
    """분산/평균. 1보다 크면 몰려 있고(사람 쪽), 1보다 작으면 고르게 깔려 있다(할당량 쪽)."""
    if len(counts) < 3:
        return 1.0
    m = sum(counts) / len(counts)
    if m == 0:
        return 1.0
    v = sum((c - m) ** 2 for c in counts) / len(counts)
    return v / m


def _cv(xs):
    if len(xs) < 2:
        return 0.0
    m = st.mean(xs)
    return st.pstdev(xs) / m if m else 0.0


def _pct(xs, q):
    if not xs:
        return 0
    s = sorted(xs)
    return s[int(q * (len(s) - 1))]


def eojeol_tail(w: str):
    w = re.sub(r'[^가-힣]', '', w)
    if len(w) < 2:
        return None
    for t in TAILS:
        if w.endswith(t) and len(w) > len(t):
            return t
    return None


def features(raw: str) -> dict:
    text = normalize(raw)
    paras = [p for p in (x.strip() for x in text.split('\n')) if p and not re.fullmatch(r'[=\-*#~ ]+', p)]
    n_chars = max(1, sum(len(p) for p in paras))
    k = 1000 / n_chars
    is_dia = [p.startswith(('"', "'", '「', '『', '<', '[')) for p in paras]
    nar = [p for p, d in zip(paras, is_dia) if not d]
    dia = [p for p, d in zip(paras, is_dia) if d]
    sents = [s for p in nar for s in split_sents(p)]
    ns = max(1, len(sents))
    sl = [len(s) for s in sents]
    pl = [len(p) for p in paras]
    ec = {}
    for s in sents:
        c = ending_class(s)
        ec[c] = ec.get(c, 0) + 1
    f = {}
    for c in ('past_da', 'nonpast_da', 'colloq', 'question', 'exclaim', 'ellipsis', 'noun_or_cut'):
        f['end_' + c] = ec.get(c, 0) / ns
    f['sent_len_mean'] = st.mean(sl) if sl else 0
    f['sent_len_cv'] = _cv(sl)
    f['sent_len_p10'] = _pct(sl, .1)
    f['sent_len_p90'] = _pct(sl, .9)
    f['sent_long60_ratio'] = sum(1 for x in sl if x >= 60) / ns
    f['sent_short12_ratio'] = sum(1 for x in sl if x <= 12) / ns
    f['para_len_mean'] = st.mean(pl) if pl else 0
    f['para_len_cv'] = _cv(pl)
    f['para_len_p90'] = _pct(pl, .9)
    f['para_one_sent_ratio'] = sum(1 for p in nar if len(split_sents(p)) == 1) / max(1, len(nar))
    f['dialogue_para_ratio'] = len(dia) / max(1, len(paras))
    f['dialogue_len_mean'] = st.mean([len(p) for p in dia]) if dia else 0
    f['dialogue_polite_ratio'] = sum(1 for p in dia if re.search(r'(요|니다|세요|죠)[.!?…~]*["\']?\s*$', p)) / max(1, len(dia))
    f['dialogue_run_max'] = _maxrun(is_dia)
    # 문장부호(1천 자당)
    for name, rx in [('excl', r'!'), ('dbl_excl', r'!!'), ('ques', r'\?'), ('interrobang', r'\?!|!\?'), ('ellipsis', r'…'),
                     ('tilde', r'~'), ('comma', r','), ('angle', r'[<>〈〉]'), ('bracket', r'[\[\]]'), ('paren', r'[()]'),
                     ('inner_dash', r'(?<=\S)[-—](?=\S)'), ('kk', r'ㅋ|ㅎ|ㅠ|ㅜ'), ('silence_line', r'^"?…+\.?"?$')]:
        f['p_' + name] = len(re.findall(rx, text, re.M)) * k
    f['prof_per_1k'] = len(PROF.findall(text)) * k
    f['simile_per_1k'] = len(SIMILE.findall(' '.join(nar))) * k
    f['conj_start_ratio'] = sum(1 for s in sents if CONJ.match(s)) / ns
    f['num_hangul_per_1k'] = len(NUM_HANGUL.findall(text)) * k
    f['digit_per_1k'] = len(re.findall(r'\d+', text)) * k
    f['latin_per_1k'] = len(re.findall(r'[A-Za-z]+', text)) * k
    f['pron_geu_per_1k'] = len(PRON_GEU.findall(' '.join(nar))) * k
    f['sense_verb_per_1k'] = len(SENSE_VERB.findall(text)) * k
    f['neg_da_per_1k'] = len(NEG_DA.findall(text)) * k
    f['hedge_per_1k'] = len(HEDGE.findall(text)) * k
    f['eye_per_1k'] = len(EYE.findall(text)) * k
    # 장치 분포(몰림 vs 고르게). 문단 6개 창으로 센다.
    win = [' '.join(paras[i:i + 6]) for i in range(0, len(paras), 6)] or ['']
    for name, rx in [('excl', r'!'), ('ques', r'\?'), ('ellipsis', r'…'), ('prof', PROF.pattern), ('simile', SIMILE.pattern),
                     ('dialogue', r'^"'), ('comma', r',')]:
        f['vmr_' + name] = math.log(_vmr([len(re.findall(rx, w, re.M)) for w in win]) + 0.1)
    f['vmr_para_len'] = math.log(_vmr(pl) + 0.1) if pl else 0
    # 어휘 반복: 같은 어절이 가까운 문장에서 다시 나오는 비율(사람은 반복을 겁내지 않고, 모델은 바꿔 말한다)
    toks = [[re.sub(r'[^가-힣]', '', w) for w in s.split()] for s in sents]
    rep = tot = 0
    for i, ws in enumerate(toks):
        near = set(w for t in toks[max(0, i - 3):i] for w in t if len(w) >= 2)
        for w in ws:
            if len(w) >= 2:
                tot += 1
                rep += w in near
    f['near_repeat_ratio'] = rep / max(1, tot)
    allw = [w for t in toks for w in t if len(w) >= 2]
    f['mattr100'] = _mattr(allw, 100)
    # 문법 꼬리 프로파일(어절 1천 개당)
    words = [w for w in re.findall(r'\S+', text)]
    nw = max(1, len(words))
    f['eojeol_per_sent'] = nw / max(1, len(sents) + len(dia))
    tc = {}
    for w in words:
        t = eojeol_tail(w)
        if t:
            tc[t] = tc.get(t, 0) + 1
    for t in TAILS:
        f['tail_' + t] = tc.get(t, 0) * 1000 / nw
    f['_chars'] = n_chars
    return f


def _maxrun(seq):
    best = run = 0
    prev = None
    for x in seq:
        run = run + 1 if x == prev and x else (1 if x else 0)
        prev = x
        best = max(best, run)
    return best


def _mattr(ws, w):
    if len(ws) <= w:
        return len(set(ws)) / max(1, len(ws))
    vals = [len(set(ws[i:i + w])) / w for i in range(0, len(ws) - w + 1, max(1, w // 4))]
    return sum(vals) / len(vals)


def chunk(text: str, lo=1600, hi=2600):
    """문단 경계를 지키며 lo~hi자 덩어리로 자른다."""
    paras = [p for p in normalize(text).split('\n') if p.strip()]
    out, cur, n = [], [], 0
    for p in paras:
        cur.append(p)
        n += len(p)
        if n >= lo:
            out.append('\n'.join(cur))
            cur, n = [], 0
    if cur and n >= lo * 0.6:
        out.append('\n'.join(cur))
    return [c for c in out if len(c) <= hi * 2]
