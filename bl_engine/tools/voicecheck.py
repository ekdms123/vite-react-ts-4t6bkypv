#!/usr/bin/env python3
"""BL VOICE ENGINE — voicecheck.py (v5)

글 한 편(장면/화)을 재서 AI 티와 목표 문체 이탈을 찾아낸다.
- 표준 라이브러리만으로 동작하고, 어느 환경에서나 같은 글에 같은 점수를 낸다.
  kiwipiepy가 있으면 품사 지표(ETM/MAG/EC)를 '참고'로만 보여 준다(점수에 넣지 않는다. v3까지는 설치 여부로 점수가 달라졌다).
- 판정의 주축은 판별기(discriminator.py): BL 원작 4종 vs AI 글로 학습한 추상 문체 모델의 P(사람 원작).
- 덩어리 단위로는 '넘치는 것'(최대치·금지 패턴)만 잡는다. '모자란 것'(최소치)은 화를 묶어 --series에서만 잰다.
  덩어리마다 최소치를 강제하면 모든 덩어리에 같은 장치가 깔리고, 그 고른 분포가 곧 AI 지문이 된다(v5 실측).
- 수치 목표는 voice/style_targets.json, 금지 패턴은 voice/banlist.json.

사용:
  python tools/voicecheck.py 원고.txt            # 사람이 읽는 리포트
  python tools/voicecheck.py 원고.txt --json     # 기계용
  python tools/voicecheck.py a.txt b.txt c.txt --rank   # 후보 중 최선 고르기 (동점이면 이슈 수, 길이 순)
  python tools/voicecheck.py 원고.txt --preset tragedy  # 장면 프리셋: comedy/tension/confession/fight/tragedy
  python tools/voicecheck.py 1화.txt 2화.txt 3화.txt --series  # 화를 가로지르는 반복 버릇
  python tools/voicecheck.py 원고.txt --card PROJECT_VOICE_CARD.md  # 손버릇 카드 적용(카드 밖 부사 금지)
  python tools/voicecheck.py 원고.txt --vocab  # BL 단어장 참고 리포트(점수 무관)
  python tools/voicecheck.py 원고.md --score HY-0128  # (v7) 리듬 악보 위에 쓴 원고: 프리셋 믹스 대신 악보 맞춤을 본다
  python tools/voicecheck.py 블로그.md --blog  # 블로그·에세이: 판별기는 참고만, 설계 티(S07~S09)는 그대로 검사
"""
from __future__ import annotations
import json, re, sys, os, signal, statistics as st
if hasattr(signal, 'SIGPIPE'):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TARGETS = json.load(open(os.path.join(ROOT, 'voice', 'style_targets.json'), encoding='utf-8'))
SERIES_MODE = False
BLOG_MODE = '--blog' in sys.argv  # 블로그·에세이: 판별기는 BL 소설 기준이라 참고로만 쓰고, B01~B03을 더 본다
try:
    sys.path.insert(0, HERE)
    import discriminator as _DISC
    _DISC.load_model()
except Exception:  # 모델 파일이 없으면 판별기 없이 패턴 검사만 한다(리포트에 표시)
    _DISC = None
BANS = json.load(open(os.path.join(ROOT, 'voice', 'banlist.json'), encoding='utf-8'))

try:
    from kiwipiepy import Kiwi  # optional
    _KIWI = Kiwi()
except Exception:
    _KIWI = None

QUOTE_OPEN = ('"', '“', '”', "'", '‘', '’', '「', '『', '<', '〈')
PROF = re.compile(r'(시발|씨발|씨팔|존나|좆|새끼(?!손|발|줄|고양|강아|돼지|오리|양|곰)|병신|지랄|썅|개같|미친놈|미친새끼|염병|빌어먹|젠장|제기랄)')
REDUP = re.compile(r'([가-힣]{1,2})\1')
SIMILE = re.compile(r'(처럼|듯이|듯한|(?<![는은을ㄹ])듯 |마치|인 양|(?<!것 )같았다|(?<!것 )같은 [가-힣]+(이|가|을|를|으로|로)?(?= ))')
PRON_GEU = re.compile(r'(?<![가-힣])그(가|는|의|를|에게|와|도) ')
EVAL_REF = re.compile(r'(녀석|놈|새끼|걔|그 애|저 애|그 인간|저 인간|그 자식)')
NEG_ACT = re.compile(r'지 않았다[.!…]*["”’]?$')


def split_sents(p: str):
    return [s.strip() for s in re.split(r'(?<=[.!?…])\s+', p) if s.strip()]


def ending_class(s: str) -> str:
    t = s.rstrip('"”’\' ')
    if t.endswith(('…', '...', '..')):
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
    if re.search(r'다$', t):
        return 'nonpast_da'
    if re.search(r'(지|네|군|나|까|야|아|어|래|걸|데|게|고|며|면서|서|니|구나|소|오|구려|느냐|거라|니라|세|잖아|거든)$', t):
        return 'colloq'
    return 'noun_or_cut'


def measure(text: str) -> dict:
    paras = [p.strip() for p in re.split(r'\n+', text) if p.strip() and p.strip() != '===']
    dia = [p for p in paras if p.startswith(QUOTE_OPEN) or p.startswith(('-', '—', 'ㅡ'))]
    dset = set(dia)
    nar = [p for p in paras if p not in dset]
    nar_text = '\n'.join(nar)
    all_text = '\n'.join(paras)
    nchar = max(1, len(nar_text)); achar = max(1, len(all_text))
    ns = [s for p in nar for s in split_sents(p)]
    tot = max(1, len(ns))
    sl = [len(s) for s in ns] or [0]
    ps = [len(split_sents(p)) for p in nar] or [0]
    ec = {}
    for s in ns:
        c = ending_class(s); ec[c] = ec.get(c, 0) + 1
    srt = sorted(sl)
    pct = lambda q: srt[int(q * (len(srt) - 1))]
    mean = st.mean(sl) if sl else 0
    f = {
        'chars': achar,
        'narr_sentences': len(ns),
        'sent_len_mean': mean,
        'sent_len_p10': pct(.1), 'sent_len_p90': pct(.9),
        'sent_len_cv': (st.pstdev(sl) / mean) if mean else 0,
        'one_sent_para_ratio': sum(1 for x in ps if x == 1) / max(1, len(ps)),
        'dialogue_para_ratio': len(dia) / max(1, len(paras)),
        'dialogue_polite_ratio': sum(1 for p in dia if re.search(r'(요|니다|세요|죠)[.!?…~]*["”’\']?\s*$', p)) / max(1, len(dia)),
        **{f'end_{k}': ec.get(k, 0) / tot for k in ['past_da', 'nonpast_da', 'colloq', 'question', 'exclaim', 'ellipsis', 'noun_or_cut']},
        'neg_action_ratio': sum(1 for s in ns if NEG_ACT.search(s)) / tot,
        'comma_sentence_share': sum(1 for s in ns if ',' in s) / tot,
        'profanity_per_10k': len(PROF.findall(all_text)) * 10000 / achar,
        'redup_per_10k': len(REDUP.findall(all_text)) * 10000 / achar,
        'simile_per_1k': len(SIMILE.findall(nar_text)) * 1000 / nchar,
        'pron_geu_per_10k': len(PRON_GEU.findall(nar_text)) * 10000 / nchar,
        'eval_ref_per_10k': len(EVAL_REF.findall(all_text)) * 10000 / achar,
        'max_same_ending_run': _max_run([ending_class(s) for s in ns]),
    }
    if _KIWI is not None and ns:
        pos = {}; n = 0
        for s in ns[:600]:
            for t in _KIWI.tokenize(s):
                pos[t.tag] = pos.get(t.tag, 0) + 1; n += 1
        n = max(1, n)
        for tag in ('ETM', 'MAG', 'EC', 'IC'):
            f[f'pos_{tag}'] = pos.get(tag, 0) / n
    f['_paras'] = paras; f['_nar'] = nar
    return f


def _max_run(seq):
    best = run = 0; prev = None
    for x in seq:
        run = run + 1 if x == prev else 1
        prev = x; best = max(best, run)
    return best


PRESET = None


def _load_examples():
    import glob
    grams = set()
    for fp in glob.glob(os.path.join(ROOT, 'voice', '*.md')):
        for line in open(fp, encoding='utf-8'):
            if not re.search(r'(예문|예\)|→|템플릿|“|")', line):
                continue
            toks = re.findall(r'[가-힣]+', line)
            for i in range(len(toks) - 3):
                g = ' '.join(toks[i:i + 4])
                if sum(len(x) for x in toks[i:i + 4]) >= 9:
                    grams.add(g)
    return grams


_EXAMPLE_GRAMS = None


def check_example_copy(text: str):
    global _EXAMPLE_GRAMS
    if _EXAMPLE_GRAMS is None:
        _EXAMPLE_GRAMS = _load_examples()
    toks = re.findall(r'[가-힣]+', text)
    hits = sorted({' '.join(toks[i:i + 4]) for i in range(len(toks) - 3)} & _EXAMPLE_GRAMS)
    if hits:
        return [{'kind': 'ban', 'id': 'E01', 'name': '엔진 문서 예문을 그대로 가져옴', 'count': len(hits), 'per_10k': 0,
                 'allowed_per_10k': 0, 'weight': 3, 'fix': '예문은 장치 설명용이다. 같은 장치를 다른 소재·다른 단어로 다시 쓴다.', 'where': hits[:6]}]
    return []


SCORE_ID = None  # (v7) 리듬 악보 ID. 악보를 따라 쓴 원고는 엔진 프리셋 믹스 대신 사람 악보를 기준으로 삼는다


def check_preset(f: dict):
    if not PRESET or SCORE_ID:
        return []
    p = TARGETS['presets'][PRESET]; out = []; tol = TARGETS['mix_tolerance']
    for key, want in zip(TARGETS['mix_keys'], p['mix']):
        v = f.get(key, 0)
        if v > want + tol or (SERIES_MODE and v < want - tol):  # v5: 덩어리에서는 넘치는 쪽만
            out.append({'kind': 'band', 'key': f'{PRESET}:{key}', 'value': round(v, 3), 'want': f"{want}±{tol}", 'weight': 1,
                        'fix': f"{p['label']} 프리셋 종결 믹스에서 벗어남. ANTI_AI_PLAYBOOK §0의 종결 바꾸기 작업으로 맞춘다."})
    lo, hi = p['simile']; v = f.get('simile_per_1k', 0)
    if (SERIES_MODE and v < lo) or v > hi:
        out.append({'kind': 'band', 'key': f'{PRESET}:simile_per_1k', 'value': round(v, 2), 'want': f'{lo}~{hi}', 'weight': 1,
                    'fix': f"{p['label']} 프리셋 비유 범위. 비극·긴장은 비유를 줄이고 하찮은 생활 사물로."})
    if f.get('profanity_per_10k', 0) > p['profanity_max']:
        out.append({'kind': 'band', 'key': f'{PRESET}:profanity_per_10k', 'value': round(f['profanity_per_10k'], 1), 'want': f"<= {p['profanity_max']}", 'weight': 1,
                    'fix': '이 프리셋에서는 욕을 줄인다.'})
    return out


def check_targets(f: dict):
    issues = []
    for key, spec in TARGETS['features'].items():
        if PRESET and key == 'simile_per_1k':
            continue
        if PRESET and key == 'profanity_per_10k':
            continue
        if key not in f or spec.get('info_only'):
            continue
        v = f[key]; lo = spec.get('min') if SERIES_MODE else None; hi = spec.get('max')
        if lo is not None and v < lo:
            issues.append({'kind': 'band', 'key': key, 'value': round(v, 4), 'want': f'>= {lo}', 'weight': spec.get('weight', 1), 'fix': spec.get('fix_low', '')})
        if hi is not None and v > hi:
            w = spec.get('weight', 1)
            if PRESET and key == 'dialogue_polite_ratio':
                w = TARGETS['presets'][PRESET]['polite_weight']
            issues.append({'kind': 'band', 'key': key, 'value': round(v, 4), 'want': f'<= {hi}', 'weight': w, 'fix': spec.get('fix_high', '')})
    return issues


CARD_ADVERBS = []


def check_bans(text: str, f: dict):
    hits = []
    lines = text.split('\n')
    for b in BANS['patterns']:
        if b.get('status') == 'anti_signal':
            continue
        regex = b['regex']
        if b['id'] == 'T01' and CARD_ADVERBS:
            # 손버릇 카드에 있는 부사는 1만 자당 4회까지 허용, 카드 밖 부사는 1회도 허용하지 않는다
            pool = re.findall(r'[가-힣]+', regex.split('(?<![가-힣])')[1])
            off = [w for w in pool if w not in CARD_ADVERBS]
            regex = r'(?<![가-힣])(' + '|'.join(off) + r')(?= )' if off else r'(?!x)x'
            b = dict(b, max_per_10k=0, name='손버릇 카드 밖의 고풍 부사')
            n_card = len(re.findall(r'(?<![가-힣])(' + '|'.join(CARD_ADVERBS) + r')(?= )', text))
            if n_card * 10000 / max(1, f['chars']) > 4:
                hits.append({'kind': 'ban', 'id': 'T01c', 'name': '카드 부사 과다', 'count': n_card, 'per_10k': 0,
                             'allowed_per_10k': 4, 'weight': 2, 'fix': '카드 부사도 화당 1~2회.', 'where': []})
        rx = re.compile(regex, re.M)
        found = []
        for i, line in enumerate(lines, 1):
            for m in rx.finditer(line):
                found.append((i, m.group(0)))
        if not found:
            continue
        per10k = len(found) * 10000 / max(1, f['chars'])
        limit = b.get('max_per_10k', 0)
        if per10k > limit:
            hits.append({'kind': 'house' if b.get('status') == 'house_rule' else 'ban', 'id': b['id'], 'name': b['name'], 'count': len(found), 'per_10k': round(per10k, 1),
                         'allowed_per_10k': limit, 'weight': b.get('weight', 1), 'fix': b.get('fix', ''),
                         'where': [f'L{i}: {s}' for i, s in found[:6]]})
    return hits


def check_scene(f: dict):
    out = []
    paras = f['_paras']
    if not paras:
        return out
    first, last = paras[0], paras[-1]
    if not first.startswith(QUOTE_OPEN) and len(split_sents(first)) == 1 and re.search(r'(생각보다|이상할 만큼|묘하게|유난히|조용했다|고요했다|가득했다)', first):
        out.append({'kind': 'scene', 'id': 'S01', 'name': '한 문장 무대 설정으로 장면을 연다', 'weight': 3,
                    'fix': '대사 한복판이나 인물의 행동/흉보기로 시작하고, 장소는 나중에 흘린다.'})
    if not last.startswith(QUOTE_OPEN) and re.search(r'(남아 있었다|여전히[^.]*지 않았다|그칠 기미가|처음으로[^.]*(생각했다|느꼈다)|아직 따뜻했다|지 않았다[.…]*$|식어 있었다|[가-힣]+ 있었다\.$)', last):
        out.append({'kind': 'scene', 'id': 'S02', 'name': '잔향 서술 한 줄로 장면을 닫는다', 'weight': 3,
                    'fix': '충격 대사/몸 동작/끊긴 회상/다음 장면으로 곧장 넘어가기 중 하나로 끝낸다.'})
    if f.get('pron_geu_per_10k', 0) > 12 and f.get('pron_geu_per_10k', 0) > 2 * max(1, f.get('eval_ref_per_10k', 0)):
        out.append({'kind': 'scene', 'id': 'S03', 'name': "상대를 중립 대명사 '그'로만 부른다", 'weight': 2,
                    'fix': '화자의 평가가 실린 지칭어(녀석/놈/걔/별명/직함)로 바꾸고, 관계 변화에 따라 지칭어를 갈아 끼운다.'})
    # S05: 같은 서술어로 끝나는 문장 3연속(경구식 삼단 반복)
    nar_s = [x for p in f['_nar'] for x in split_sents(p)]
    tails = [re.sub(r'[^가-힣]', '', ' '.join(x.split()[-1:])) for x in nar_s]
    for i in range(len(tails) - 2):
        if tails[i] and len(tails[i]) >= 3 and tails[i] == tails[i + 1] == tails[i + 2]:
            out.append({'kind': 'scene', 'id': 'S05', 'name': f"같은 서술어 3연속 반복('{tails[i]}')", 'weight': 2,
                        'fix': '경구식 삼단 반복은 AI 표지다. 두 번에서 끊거나 세 번째를 엉뚱하게 비튼다.'}); break
    # S06: 문장 골격(마지막 두 어절) 재사용
    sk = {}
    for x in nar_s:
        w = x.split()
        if len(w) >= 4:
            key = ' '.join(w[-2:]).strip('.!?…"”')
            sk[key] = sk.get(key, 0) + 1
    rep = [k for k, v in sk.items() if v >= 3 and len(k) >= 6]
    if rep:
        out.append({'kind': 'scene', 'id': 'S06', 'name': '같은 문장 골격 3회 이상: ' + ', '.join(rep[:3]), 'weight': 2,
                    'fix': '같은 마무리 어절을 반복하지 않는다.'})
    out += check_design(f)
    if f.get('max_same_ending_run', 0) >= TARGETS.get('same_ending_run_max', 8):
        out.append({'kind': 'scene', 'id': 'S04', 'name': f"같은 종결 유형 {f['max_same_ending_run']}연속", 'weight': 2,
                    'fix': '현재형 판정, 명사 종결, 의문, 구어 종결을 끼워 리듬을 깬다.'})
    return out


# (v6) 설계 티: 단어가 아니라 문단 설계에서 나는 AI 냄새. BL 원작 4종 덩어리에서 S07·S08은 0.2%, S09(공유 소재 11개 이상)는 1% 미만.
APHORISM_HEAD = re.compile(r'^(사람은|사람들은|사람이란|글은|글이란|남이 [가-힣 ]{1,12}(은|는)|누구나|인생은|사랑은|세상은|([가-힣]+ ){0,2}[가-힣]+(은|는) 원래)')
APHORISM_END = re.compile(r'(는다|ㄴ다|한다|이다|있다|없다|된다|만든다|시킨다|법이다|마련이다|재밌다|좋다)[.!]?$')
FIRST_PERSON = re.compile(r'(나는|나도|내가|내 |저는|제가)')
CALLBACK = re.compile(r'(다 쓰고 보니|쓰고 보니|알고 보니|돌이켜 보면|결국 (같은|다|하나|그)[^.]{0,20}(얘기|이야기|였다|이었다))')
_DESIGN_STOP = set('그리고 그런데 그래서 하지만 그냥 정말 진짜 너무 조금 다시 이미 아직 오늘 그게 이게 그것 이것 하나 사람 거다 것이 것을 것은 있었다 없었다 했다 하는 있는 같은'.split())


def _stems(p):
    from stylofeat import TAILS
    out = set()
    for w in p.split():
        w = re.sub(r'[^가-힣]', '', w)
        for t in TAILS:
            if w.endswith(t) and len(w) - len(t) >= 2:
                w = w[:-len(t)]; break
        if len(w) >= 2 and w not in _DESIGN_STOP:
            out.add(w)
    return out


def check_design(f: dict):
    out = []
    nar = f['_nar']
    sents = [x for p in nar for x in split_sents(p)]
    aph = [x for x in sents if APHORISM_HEAD.search(x) and APHORISM_END.search(x) and not FIRST_PERSON.search(x)]
    if aph:
        out.append({'kind': 'scene', 'id': 'S07', 'name': '교훈 문장(일반 주어로 세상 이치를 정리): ' + aph[0][:30], 'weight': 3,
                    'fix': '내 얘기를 세상 이치로 바꾸지 않는다. 지우거나 "나는 ~했다"로 되돌린다.'})
    if CALLBACK.search('\n'.join(nar)):
        out.append({'kind': 'scene', 'id': 'S08', 'name': "회수 요약('다 쓰고 보니/결국 같은 얘기')", 'weight': 3,
                    'fix': '앞에 깔아 둔 것을 끝에서 다시 묶어 보여 주지 않는다. 묶는 문장을 지운다.'})
    ps = [p for p in nar if len(split_sents(p)) >= 3]
    best = 0
    for i in range(len(ps)):
        for j in range(i + 1, min(len(ps), i + 3)):
            best = max(best, len(_stems(ps[i]) & _stems(ps[j])))
    if best >= TARGETS.get('mirror_shared_max', 11):
        out.append({'kind': 'scene', 'id': 'S09', 'name': f'거울 구조(가까운 두 문단이 같은 소재 {best}개를 되받음)', 'weight': 3,
                    'fix': '대구로 맞춘 두 문단 중 하나를 다른 소재로 다시 쓰거나, 길이를 확 다르게 한다.'})
    return out


# (v6) 블로그·에세이 모드 전용 검사. 블로그 원문 말뭉치로 잰 값이 아니라 사용자 피드백에서 나온 잠정 규칙이다.
WRITTEN_END = re.compile(r'(것이다|법이다|마련이다|곤 했다|터였다|셈이었다|뿐이다|따름이다)[.!]?$')
SEO_INSERT = re.compile(r'(검색(하면|해 보면|해보면|창에|해 봤|해봤)|검색어|키워드)')
SEASON_CLICHE = ['낙엽', '은행잎', '단풍잎', '하늘이 높', '높은 하늘', '선선한 바람', '옷깃', '트렌치', '바바리', '캔커피',
                 '코스모스', '갈대', '독서의 계절', '천고마비', '니트', '쓸쓸한 바람']


def check_blog(f: dict):
    out = []
    sents = [x for p in f['_nar'] for x in split_sents(p)]
    we = [x for x in sents if WRITTEN_END.search(x)]
    if len(we) >= 2:
        out.append({'kind': 'scene', 'id': 'B01', 'name': f"문어체 종결 {len(we)}회(~것이다/~법이다/~곤 했다)", 'weight': 2,
                    'fix': '블로그는 말하듯 끝낸다. ~했다/~함/~임/~거다로.'})
    seo = [x for x in sents if SEO_INSERT.search(x)]
    if seo:
        out.append({'kind': 'scene', 'id': 'B02', 'name': '검색어를 넣으려고 만든 문장: ' + seo[0][:30], 'weight': 3,
                    'fix': '키워드는 제목 앞부분, 본문에 문맥상 한 번, 해시태그로만. "~를 검색하면" 문장은 지운다.'})
    allt = '\n'.join(f['_paras'])
    hits = [w for w in SEASON_CLICHE if w in allt]
    if len(hits) >= 3:
        out.append({'kind': 'scene', 'id': 'B03', 'name': '계절 소품 클리셰 묶음(잠정 목록): ' + ', '.join(hits[:5]), 'weight': 2,
                    'fix': '모두가 쓰는 가을 소품 대신 내가 실제로 한 짓 하나로 바꾼다.'})
    return out


def _strip_blog_markup(text: str) -> str:
    lines = []
    for ln in text.split('\n'):
        st_ = ln.strip()
        if st_.startswith('제목:') or re.fullmatch(r'(#\S+\s*)+', st_):
            continue  # 제목 줄과 해시태그 줄은 본문이 아니다
        lines.append(re.sub(r'^(#{1,6}\s+|>\s*)', '', st_))
    return '\n'.join(lines)


def score(text: str):
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)  # 파일 머리 주석은 본문이 아니다
    text = _strip_blog_markup(text)
    f = measure(text)
    issues = check_targets(f) + check_preset(f) + check_bans(text, f) + check_scene(f) + check_example_copy(text)
    if BLOG_MODE:
        issues += check_blog(f)
    penalty = 0.0
    for it in issues:
        w = it.get('weight', 1)
        if it['kind'] == 'house':
            continue  # 작가 개인 원칙: 보여 주되 AI 점수에는 넣지 않는다
        if it['kind'] == 'ban':
            penalty += w * min(4, 1 + it['count'] / 3)
        else:
            penalty += w * 2
    ai_score = min(100.0, penalty)
    f['pos_checked'] = _KIWI is not None
    disc = _DISC.score_text(text) if _DISC else None
    f['_disc'] = disc
    p_ok = disc is None or BLOG_MODE or disc['p_human_min'] >= TARGETS.get('p_human_threshold', 0.5)
    if disc is not None:
        disc['outside_max'] = max(len(c['outside_human_range']) for c in disc['chunks'])  # 안내용(합격 조건 아님)
    r_ok = True
    if SCORE_ID:
        import rhythm_score as _rs
        f['_rhythm'] = _rs.fit_text(text, SCORE_ID)
        r_ok = f['_rhythm']['pass']
    verdict = 'PASS' if ai_score <= TARGETS['pass_threshold'] and p_ok and r_ok else 'REWRITE'
    if disc is None:
        verdict += ' (판별기 모델 없음: 패턴 검사만)'
    if f['chars'] < 1500:
        verdict += ' (1,500자 미만: 수치 신뢰도 낮음, 덩어리 기준 1,800~2,500자)'
    return f, issues, round(ai_score, 1), verdict


SERIES_WATCH = re.compile(r'(?<![가-힣])(퍽|구태여|잠자코|별안간|자못|짐짓|하릴없이|염병|늦었다)')


def series_report(paths):
    """여러 화를 같이 넣으면, 화를 가로질러 반복되는 버릇(블라인드 판별자가 잡은 종류)을 찾는다."""
    texts = [open(p, encoding='utf-8').read() for p in paths]
    print('=== 연재 버릇 검사 (화를 가로지르는 반복)')
    from collections import defaultdict
    where = defaultdict(set)
    for i, t in enumerate(texts):
        for m in SERIES_WATCH.finditer(t):
            where[m.group(1)].add(i)
        for m in SIMILE.finditer(t):
            ctx = t[max(0, m.start() - 8):m.start()]
            noun = re.findall(r'[가-힣]{2,}', ctx)
            if noun:
                where['직유:' + noun[-1]].add(i)
        for x in split_sents(t):
            w = x.split()
            if len(w) >= 4:
                where['골격:' + ' '.join(w[-2:]).strip('.!?…"”')].add(i)
    n = len(texts); bad = 0
    for k, v in sorted(where.items(), key=lambda kv: -len(kv[1])):
        if len(v) >= max(2, (n + 1) // 2) and (not k.startswith('골격:') or len(k) >= 9):
            print(f'  [반복] {k}  → {len(v)}/{n}화'); bad += 1
    print('반복 버릇 없음' if not bad else f'반복 버릇 {bad}개: 다음 화에서는 이 단어·직유·문장 골격을 쓰지 않는다.')
    # (v5) 최소치는 화를 묶은 전체에서만 잰다
    global SERIES_MODE
    SERIES_MODE = True
    f = measure('\n'.join(texts))
    lows = [it for it in check_targets(f) if it['want'].startswith('>=')]
    SERIES_MODE = False
    print('=== 연재 전체 최소치(덩어리마다 강제하지 않는다)')
    for it in lows:
        print(f"  [부족] {it['key']} = {it['value']} (목표 {it['want']}) → {it['fix']}")
    if not lows:
        print('  부족한 항목 없음')
    device_spread_report(texts)


def device_spread_report(texts):
    """(v5) 장치가 덩어리마다 고르게 깔렸는지 잰다. 사람 원작은 장치를 몇 덩어리에 몰아 쓰고 나머지는 비운다."""
    from stylofeat import chunk, normalize
    spec = TARGETS.get('device_presence', {})
    if not spec:
        return
    chunks = [c for t in texts for c in (chunk(t) or [normalize(t)])]
    if len(chunks) < 4:
        print('=== 장치 분포: 덩어리 4개 이상부터 잰다'); return
    print(f'=== 장치 분포 ({len(chunks)}덩어리. 원작 작품별 등장률과 비교)')
    flagged = 0
    for name, d in spec.items():
        if name.startswith('_'):
            continue
        rx = re.compile(d['pattern'], re.M)
        rate = sum(1 for c in chunks if rx.search(c)) / len(chunks)
        hi = max(d['human_presence_by_work'])
        med = d['human_presence_median']
        msg = ''
        if rate > hi + 0.1:
            msg = f'원작 최고 작품({hi:.0%})보다 자주 깔림 → 이 장치는 몇 장면에 몰고 나머지는 0으로'
        elif d.get('signature') and 0 < rate < 0.08 and len(chunks) >= 8:
            msg = '켜 놓은 장치가 거의 안 보임(작품 지문이면 꾸준히, 아니면 카드에서 끈다)'
        if msg:
            flagged += 1
            print(f"  [분포] {d.get('label', name)} 등장 {rate:.0%} (원작 중앙 {med:.0%}) → {msg}")
    on = [sum(1 for name, d in spec.items() if not name.startswith('_') and d.get('signature') and re.search(d['pattern'], c, re.M)) for c in chunks]
    if on and sum(on) / len(on) > TARGETS.get('signature_devices_per_chunk_max', 1.9):
        flagged += 1
        print(f'  [분포] 덩어리당 시그니처 장치 평균 {sum(on)/len(on):.2f}개 (원작 약 1.5) → 장치 없는 덩어리를 늘린다')
    if not flagged:
        print('  고르게 깔린 장치 없음')


def vocab_report(text: str):
    """BL_VOCAB 참고 리포트(점수에 영향 없음). Claude 쪽 단어와 대체어, 원작 태도 부사 사용 현황을 보여 준다."""
    vp = os.path.join(ROOT, 'voice', 'bl_vocab.json')
    if not os.path.exists(vp):
        return
    V = json.load(open(vp, encoding='utf-8'))
    n = max(1, len(text))
    print('--- 어휘 참고 (BL_VOCAB, 점수와 무관)')
    for w, cl, bl, alt in [(r[0], r[1], r[2], r[3]) for r in V['avoid_adverbs']]:
        key = re.sub(r'\(.*?\)', '', w)
        c = len(re.findall(re.escape(key), text))
        if c and c * 10000 / n > bl * 2:
            print(f'  [Claude쪽] {w} ×{c} (원작 {bl}/만자) → {alt}')
    for row in V['avoid_nouns']:
        for w in re.split(r'[·()]', row[0]):
            w = w.strip()
            if len(w) >= 2 and len(re.findall(re.escape(w), text)) >= 2:
                print(f'  [Claude쪽] {w} ×{len(re.findall(re.escape(w), text))} → {row[2]}')
    used = [r[0] for r in V['attitude_adverbs'] if any(x in text for x in r[0].split('·'))]
    print(f"  [원작쪽] 태도 부사 사용: {', '.join(used) if used else '없음'} (끼워 넣지 말 것. 카드 범위에서 장면에 맞을 때만)")


def report(path: str, as_json=False):
    text = open(path, encoding='utf-8').read()
    f, issues, s, verdict = score(text)
    pub = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in f.items() if not k.startswith('_')}
    if as_json:
        print(json.dumps({'file': path, 'ai_score': s, 'verdict': verdict, 'discriminator': f.get('_disc'), 'metrics': pub, 'issues': issues}, ensure_ascii=False, indent=1))
        return s
    d = f.get('_disc')
    print(f'=== {path}\nAI_SCORE {s} (패턴 점수, 낮을수록 좋음, 통과 기준 {TARGETS["pass_threshold"]})  → {verdict}')
    if d and BLOG_MODE:
        print(f"P_HUMAN {d['p_human_mean']} (--blog: BL 소설 원작 기준 모델이라 블로그에서는 참고만, 판정에 쓰지 않는다)")
    elif d:
        print(f"P_HUMAN {d['p_human_mean']} (덩어리 최저 {d['p_human_min']}, 통과 기준 {TARGETS.get('p_human_threshold', 0.5)})"
              f"  원작 범위 이탈 {d['outside_max']}개 (원작 덩어리 중앙값 6. {TARGETS.get('outside_range_max', 9)}개를 넘고 고친 뒤 늘었다면 과잉 교정 의심)")
    for c in (d['chunks'] if d and not BLOG_MODE else []):
        for it in c['push_ai'][:4]:
            print(f"[판별] {it['diagnosis']} ({it['feature']}={it['value']}, 원작 평균 {it['human_mean']}) → {it['fix']}")
        for it in c['outside_human_range'][:3]:
            print(f"[과잉/이탈] {it['feature']}={it['value']} 원작 범위 {it['human_p05']}~{it['human_p95']} 밖")
    if not pub.get('pos_checked'):
        print('  (kiwipiepy 없음: 품사 참고 지표 생략. 점수와 무관)')
    print(f"글자 {pub['chars']} / 서술문 {pub['narr_sentences']}")
    for key in ['end_past_da', 'end_nonpast_da', 'end_colloq', 'end_question', 'end_noun_or_cut', 'sent_len_cv', 'sent_len_p90', 'neg_action_ratio', 'simile_per_1k', 'profanity_per_10k', 'pos_ETM', 'pos_MAG']:
        if key in pub:
            print(f'  {key:22s} {pub[key]}')
    issues.sort(key=lambda x: -x.get('weight', 1))
    for it in issues:
        if it['kind'] == 'band':
            print(f"[수치] {it['key']} = {it['value']} (목표 {it['want']}) → {it['fix']}")
        elif it['kind'] in ('ban', 'house'):
            tag = '작가 원칙' if it['kind'] == 'house' else '금지'
            print(f"[{tag}] {it['id']} {it['name']} ×{it['count']} → {it['fix']}")
            for w in it['where']:
                print(f'        {w}')
        else:
            print(f"[장면] {it['id']} {it['name']} → {it['fix']}")
    if SCORE_ID:
        r = f['_rhythm']
        print(f"[악보] {SCORE_ID} 맞춤 {r['fit']} (기준 {r['threshold']}) → {'PASS' if r['pass'] else 'REWRITE'}  "
              f"문단 순서 {r['type_seq']} · 종결 순서 {r['endings']} · 문장 길이 {r['lengths']} · 장치 위치 {r['devices']}")
    if '--vocab' in sys.argv:
        vocab_report(text)
    return s


if __name__ == '__main__':
    argv = sys.argv[1:]
    if '--card' in argv:
        i = argv.index('--card'); cp = argv[i + 1]; del argv[i:i + 2]
        m = re.search(r'\| 고풍 부사 \| ([^|]+) \|', open(cp, encoding='utf-8').read())
        if m:
            CARD_ADVERBS[:] = [w.strip() for w in m.group(1).split(',') if w.strip()]
    if '--score' in argv:
        i = argv.index('--score'); SCORE_ID = argv[i + 1]; del argv[i:i + 2]
    if '--preset' in argv:
        i = argv.index('--preset'); PRESET = argv[i + 1]; del argv[i:i + 2]
        if PRESET not in TARGETS['presets']:
            print('preset은', list(TARGETS['presets']), '중 하나'); sys.exit(2)
    args = [a for a in argv if not a.startswith('--')]
    if not args:
        print(__doc__); sys.exit(1)
    if '--series' in sys.argv:
        series_report(args); sys.exit(0)
    if '--rank' in sys.argv:
        rows = []
        for p in args:
            f_, iss, s, v = score(open(p, encoding='utf-8').read())
            ph = f_['_disc']['p_human_min'] if f_.get('_disc') else 0.0
            rows.append((not v.startswith('PASS'), -ph, s, len(iss), -f_['chars'], p, v))
        rows.sort()
        for fail, nph, s, n, _, p, v in rows:
            print(f'{s:6.1f}  P_HUMAN {-nph:.3f}  {v[:6]:6s}  issues={n:2d}  {p}')
        print(f'BEST: {rows[0][5]}')
    else:
        for p in args:
            report(p, '--json' in sys.argv)
