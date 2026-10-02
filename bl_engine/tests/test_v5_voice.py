"""목소리 층 v5 회귀 테스트: 환경 독립 점수, 판별기, 덩어리 최소치 제거, 장치 지문, 원작 유출 방지."""
import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import voicecheck as vc
import discriminator as dz
import stylofeat as sf

SAMPLES = ROOT / 'verify' / 'bl_samples'


def _txt(name):
    return next(SAMPLES.glob(name)).read_text(encoding='utf-8')


def test_score_does_not_depend_on_kiwipiepy():
    # v3 버그: kiwipiepy 설치 여부로 같은 글이 4.0 / 0.0을 받았다
    text = _txt('V3_*.md')
    saved = vc._KIWI
    try:
        vc._KIWI = None
        a = vc.score(text)
        vc._KIWI = saved
        b = vc.score(text)
    finally:
        vc._KIWI = saved
    assert a[2] == b[2] and a[3] == b[3]


def test_old_engine_samples_rewrite_and_v5_samples_are_hard_negatives():
    for p in SAMPLES.glob('V[123]_*.md'):
        assert vc.score(p.read_text(encoding='utf-8'))[3].startswith('REWRITE'), p.name
    # v7: v5 시험 장면은 판별기를 통과했던 글이라 적대적 재학습에서 AI 쪽 학습 데이터로 들어갔다
    m = json.loads((ROOT / 'voice/discriminator_model.json').read_text(encoding='utf-8'))
    assert any('V5_' in g for g in m['eval']['per_group_mean_p_human'])
    for p in SAMPLES.glob('V5_*.md'):
        assert vc.score(p.read_text(encoding='utf-8'))[3].startswith('REWRITE'), p.name


def test_html_comment_header_is_not_scored():
    text = _txt('V5_시험장면1_*.md')
    body = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    assert vc.score(text)[2] == vc.score(body)[2]


def test_model_matches_feature_extractor_and_has_no_source_text():
    m = json.loads((ROOT / 'voice/discriminator_model.json').read_text(encoding='utf-8'))
    keys = sorted(k for k in sf.features('가나다라. 마바사.') if not k.startswith('_'))
    assert m['features'] == keys
    n = len(keys)
    assert all(len(m[k]) == n for k in ('mean', 'std', 'coef', 'human_means', 'human_p05', 'human_p95'))
    # 모델에 들어 있는 한글은 문법 꼬리 특징 이름과 설명문뿐이어야 한다
    hangul = set(re.findall(r'[가-힣]+', json.dumps({k: v for k, v in m.items() if k not in ('note', 'eval')}, ensure_ascii=False)))
    allowed = set(sf.TAILS)
    assert hangul <= allowed, hangul - allowed
    assert m['eval']['auc'] >= 0.9


def test_chunk_level_has_no_minimum_bands_but_series_does():
    flat = '그는 웃었다. 그는 갔다. 그는 왔다. 그는 앉았다. ' * 60
    keys = {i.get('key') for i in vc.check_targets(vc.measure(flat))}
    assert not any(i['want'].startswith('>=') for i in vc.check_targets(vc.measure(flat)))
    vc.SERIES_MODE = True
    try:
        lows = [i for i in vc.check_targets(vc.measure(flat)) if i['want'].startswith('>=')]
    finally:
        vc.SERIES_MODE = False
    assert lows and keys is not None


def test_anti_signal_and_house_rule_bans():
    b = {p['id']: p for p in json.loads((ROOT / 'voice/banlist.json').read_text(encoding='utf-8'))['patterns']}
    assert b['C21']['status'] == 'anti_signal' and b['C26']['status'] == 'anti_signal'
    assert b['C25']['status'] == 'house_rule'
    text = '그가 문을 열기 시작했다. ' * 3
    issues = vc.check_bans(text, vc.measure(text))
    house = [i for i in issues if i['id'] == 'C25']
    assert house and house[0]['kind'] == 'house'
    _, _, s_with, _ = vc.score('나는 밥을 먹기 시작했다. 맛이 없었다.')
    _, _, s_without, _ = vc.score('나는 밥을 먹었다. 맛이 없었다.')
    assert s_with == s_without  # 작가 원칙은 표시만, AI 점수에는 넣지 않는다


def test_measured_motion_cliches_fire():
    _, issues, _, _ = vc.score('나는 그대로 굳었다. 그는 대답하지 않았다. 창 너머로 비가 왔다. 쓸쓸한 웃음이었다.')
    ids = {i.get('id') for i in issues}
    assert {'K01', 'K02', 'K05', 'K06'} <= ids


def test_voice_card_device_fingerprint_is_consistent():
    for t in ['작품A', '작품B', '작품C', '작품D', '작품E', '작품F', '작품G']:
        out = subprocess.run([sys.executable, str(ROOT / 'tools/voice_seed.py'), t], capture_output=True, text=True).stdout
        rows = dict(re.findall(r"^\| ([^|]+?) \| (켬|끔) \|", out, re.M))
        assert sum(1 for v in rows.values() if v == '켬') >= 2
        if rows.get('침묵 줄 “…….”') == '끔':
            assert '침묵 사다리' not in out
        if rows.get("'!!'") == '끔':
            assert '느낌표 연타' not in out
        if rows.get('욕') == '끔':
            assert '(이 작품은 끔)' in out


def test_series_reports_distribution():
    texts = [p for p in SAMPLES.glob('V*.md')]
    out = subprocess.run([sys.executable, str(ROOT / 'tools/voicecheck.py'), *map(str, texts), '--series'], capture_output=True, text=True).stdout
    assert '연재 전체 최소치' in out and '장치 분포' in out


def test_slop_forensics_port_matches_upstream_semantics():
    import slop_forensics_ko as k
    r = k.find_over_represented_words({'가': 0.2, '나': 0.1}, {'가': 0.1, '나': 0.001}, 5)
    assert [w for w, *_ in r] == ['나', '가'] and abs(r[0][1] - 100) < 1e-9


def test_discriminator_explains_ai_push():
    r = dz.score_chunk(_txt('V3_*.md'))
    assert r['p_human'] < 0.5 and r['push_ai'] and all(it['fix'] for it in r['push_ai'])
