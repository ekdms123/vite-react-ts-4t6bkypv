#!/usr/bin/env python3
"""BL VOICE ENGINE — discriminator.py

학습된 추상 문체 판별기로 '사람 BL 원작일 확률'을 잰다. 표준 라이브러리만 쓴다.

  python tools/discriminator.py 원고.md            # 확률 + AI 쪽으로 미는 특징 상위 + 고치는 법
  python tools/discriminator.py 원고.md --json

판정은 덩어리(1,600~2,600자) 단위가 가장 정확하다. 긴 글은 덩어리로 잘라 각각 잰다.
주의: 이 확률은 '고칠 방향'을 알려 주는 계기판이다. 특징을 직접 맞추려고 조사·쉼표를 끼워 넣으면
(굿하트) 원작 범위(p05~p95)를 넘어서고, 그때는 [과잉 교정] 경고가 뜬다.
"""
from __future__ import annotations
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from stylofeat import features, chunk  # noqa: E402

MODEL_PATH = os.path.join(os.path.dirname(HERE), 'voice', 'discriminator_model.json')
_M = None

# 특징군 → 사람이 읽는 진단과 고치는 법. (방향: 'low' = 원작보다 낮아서 AI 쪽, 'high' = 높아서 AI 쪽)
FIX = {
    'sent_len_mean': ('문장이 짧다', '두 문장을 관형절(-던/-는)이나 연결어미(-는데/-지만/-면서)로 묶는다. 원작 서술문 평균은 약 30자다.'),
    'sent_len_p90': ('긴 문장이 없다', '문단마다 50자 넘는 압력 장문을 하나쯤 둔다.'),
    'sent_long60_ratio': ('60자 넘는 장문이 없다', '관형절 두 겹짜리 장문을 한 번 쓴다.'),
    'sent_short12_ratio': ('12자 이하 단문 연타 과다', '단문은 충격 지점에만 남기고 나머지는 이어 붙인다.'),
    'eojeol_per_sent': ('문장당 어절이 적다', '수식어·부사절을 붙여 문장에 정보를 더 싣는다.'),
    'para_len_mean': ('문단이 짧다', '서술 문단에 3~5문장을 담는다. 한 줄 문단은 쪼개 놓은 리듬 티가 난다.'),
    'para_len_p90': ('긴 문단이 없다', '한 장면에 꽉 찬 서술 문단(140자 이상) 한두 개를 둔다.'),
    'para_one_sent_ratio': ('한 문장짜리 문단 과다', '한 줄 문단을 앞뒤 문단에 합친다.'),
    'dialogue_len_mean': ('대사가 짧은 탁구뿐이다', '한 사람이 두세 문장을 몰아서 하는 대사를 넣는다(원작 대사 평균 약 25자).'),
    'dialogue_para_ratio': ('대사 문단 비율이 원작과 다르다', '대사 탁구를 줄이고 서술 문단에 말을 흡수한다.'),
    'tail_었다': ("'-었다' 꼬리 과다", '현재형 판정, 관형절, 연결어미로 문장 끝을 바꾼다.'),
    'tail_였다': ("'-였다' 꼬리 과다", '명사 판정 뒤 -였다를 줄이고 -이다/명사 종결로.'),
    'tail_다': ("'-다' 종결 과다", '연결어미로 문장을 이어 마침표 수를 줄인다.'),
    'end_past_da': ('과거 평서 종결 과다', '비과거 판정·의문·구어 종결을 섞는다.'),
    'tail_의': ("'의' 구문 부족", '소유·관계 구문(누구의 무엇)을 쓴다. AI는 관계를 문장으로 풀어 버린다.'),
    'tail_에게': ("'에게/한테' 부족", '행위의 방향(누구에게)을 문장 안에 둔다.'),
    'tail_처럼': ('비유 꼬리 부족', '생활 사물 직유를 한 번 쓴다.'),
    'simile_per_1k': ('비유가 거의 없다', '하찮은 생활 사물이나 제도 프레임으로 직유 하나.'),
    'tail_지만': ('양보·대조 연결 부족', "'-지만'으로 두 생각을 한 문장에 엮는다."),
    'tail_하고': ("'하고' 나열 부족", '구어 나열(A하고 B)을 쓴다.'),
    'tail_도': ("'도' 부족", '첨가·양보의 도를 쓴다(그것도, 나도).'),
    'tail_을': ('목적어 구문 부족', '동사에 목적어를 붙여 행위를 구체화한다.'),
    'tail_에서': ("'에서' 과다(장소 지문)", '장소 설명을 줄이고 행동으로 들어간다.'),
    'tail_부터': ("'부터' 과다", '시간 순서 설명을 줄인다.'),
    'num_hangul_per_1k': ('숫자·단위 정밀 추적(AI 지문)', '삼 년·두 시·여섯 시간 같은 수치를 지운다. 원작은 숫자를 거의 세지 않는다.'),
    'digit_per_1k': ('아라비아 숫자 과다', '수치를 지우거나 말로 뭉갠다(한참, 며칠).'),
    'neg_da_per_1k': ("'~지 않았다' 과다", '하지 않은 행동 대신 한 행동을 쓴다.'),
    'p_ques': ('물음표가 적다', '서술 속 자문을 연달아 던진다.'),
    'p_comma': ('쉼표 습관이 원작과 다르다', '쉼표 대신 연결어미로 잇거나, 반대로 너무 없으면 숨 쉴 자리를 둔다.'),
    'hedge_per_1k': ('완충 부사 과다(조금·아주·천천히·생각보다)', '정도 부사를 지운다.'),
    'eye_per_1k': ('시선·고개 지문 과다', '시선 교환 대신 손이 하는 일을 쓴다.'),
    'sense_verb_per_1k': ("'느꼈다/깨달았다/알 수 없었다' 과다", '인식 동사를 지우고 인식한 내용을 바로 쓴다.'),
    'pron_geu_per_1k': ("'그가/그는' 과다", '화자의 평가가 실린 지칭어로 바꾼다.'),
    'conj_start_ratio': ('접속사로 시작하는 문장 과다', '그리고/하지만을 지운다.'),
    'mattr100': ('어휘 다양도가 원작과 다르다', '같은 대상을 굳이 바꿔 부르지 말고, 반대로 같은 동사만 반복하지 말 것.'),
    'near_repeat_ratio': ('가까운 문장 사이 단어 반복이 적다', '같은 단어를 바꿔 말하지 말고 그대로 다시 쓴다. 동의어 돌려막기는 AI 습관이다.'),
    'prof_per_1k': ('욕 밀도가 원작과 다르다', '욕은 몇몇 장면에 몰아서 쓰고, 나머지 장면에서는 0으로 둔다.'),
    'p_silence_line': ('침묵 줄(“…….”)이 매 장면에 있다', '침묵 줄은 대치 장면에만 몰아 쓴다.'),
    'p_dbl_excl': ("'!!' 밀도가 원작과 다르다", "'!!'는 코미디 장면에 몰아 쓰고 나머지는 0."),
    'p_ellipsis': ('말줄임 밀도가 원작과 다르다', '말줄임은 대사 끝 망설임에만.'),
}
FAMILY_DEFAULT = ('원작과 다른 분포', '원작 범위 안으로 되돌린다.')


def load_model(path=MODEL_PATH):
    global _M
    if _M is None:
        _M = json.load(open(path, encoding='utf-8'))
    return _M


def score_chunk(text: str, model=None):
    m = model or load_model()
    f = features(text)
    z = 0.0
    contrib = []
    over = []
    for i, name in enumerate(m['features']):
        x = f.get(name, 0.0)
        zz = (x - m['mean'][i]) / (m['std'][i] or 1)
        c = m['coef'][i] * zz
        z += c
        contrib.append((c, name, x, m['human_means'][i]))
        lo, hi = m.get('human_p05', [None] * len(m['features']))[i], m.get('human_p95', [None] * len(m['features']))[i]
        if lo is not None and (x < lo or x > hi) and abs(m['coef'][i]) > 0.08:
            over.append((name, x, lo, hi))
    z += m['intercept']
    p = 1 / (1 + math.exp(-z))
    contrib.sort()
    push_ai = []
    for c, name, x, hm in contrib[:8]:
        if c >= -0.05:
            break
        key = name if name in FIX else None
        diag, fix = FIX.get(key, FAMILY_DEFAULT) if key else (f'{name}', FAMILY_DEFAULT[1])
        push_ai.append({'feature': name, 'value': round(x, 3), 'human_mean': round(hm, 3), 'push': round(c, 3), 'diagnosis': diag, 'fix': fix})
    return {'p_human': round(p, 4), 'chars': f['_chars'], 'push_ai': push_ai,
            'outside_human_range': [{'feature': n, 'value': round(x, 3), 'human_p05': lo, 'human_p95': hi} for n, x, lo, hi in over]}


def score_text(text: str, model=None):
    cs = chunk(text, lo=1600) if len(text) > 3400 else [text]
    rs = [score_chunk(c, model) for c in cs]
    ps = [r['p_human'] for r in rs]
    return {'p_human_min': min(ps), 'p_human_mean': round(sum(ps) / len(ps), 4), 'chunks': rs}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print(__doc__); sys.exit(1)
    m = load_model()
    for p in args:
        r = score_text(open(p, encoding='utf-8').read(), m)
        if '--json' in sys.argv:
            print(json.dumps({'file': p, **r}, ensure_ascii=False, indent=1)); continue
        print(f"=== {p}\nP(사람 원작) 평균 {r['p_human_mean']} / 최저 덩어리 {r['p_human_min']}   (0.5 이상이 목표, 모델 LOGO AUC {m['eval']['auc']})")
        for i, c in enumerate(r['chunks'], 1):
            print(f"  덩어리 {i}: {c['p_human']}  ({c['chars']}자)")
            for it in c['push_ai'][:5]:
                print(f"    [AI 쪽] {it['diagnosis']}: {it['feature']}={it['value']} (원작 평균 {it['human_mean']}) → {it['fix']}")
            for it in c['outside_human_range'][:4]:
                print(f"    [원작 범위 밖] {it['feature']}={it['value']} (원작 {it['human_p05']}~{it['human_p95']})")


if __name__ == '__main__':
    main()
