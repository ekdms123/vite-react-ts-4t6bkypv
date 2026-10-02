"""목소리 층 v7 회귀 테스트: 리듬 악보 서고(단어 없음), 고르기, 맞춤, voicecheck --score, 카드의 리듬 원천."""
import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import rhythm_score as rs
import voicecheck as vc

SAMPLES = ROOT / 'verify' / 'bl_samples'


def test_library_has_no_source_words_and_four_bl_sources():
    raw = (ROOT / 'voice/rhythm_scores.json').read_text(encoding='utf-8')
    lib = json.loads(raw)
    hangul = set(re.findall(r'[가-힣]+', raw))
    assert hangul <= set(re.findall(r'[가-힣]+', lib['note'])), hangul
    assert {k.split('-')[0] for k in lib['scores']} == {'MW', 'HY', 'SD', 'CS'}
    assert len(lib['scores']) >= 400
    cal = lib['calibration']
    assert cal['pass'] > cal['random_pair_fit_p99'] >= cal['random_pair_fit_p50']


def test_skeleton_self_fit_is_perfect_and_render_lists_every_paragraph():
    lib = rs.load_lib()
    sid, sk = next(iter(lib['scores'].items()))
    assert rs.fit_skeletons(sk, sk)['fit'] == 1.0
    out = rs.render(sid, sk)
    assert len([l for l in out.splitlines() if l.startswith('¶')]) == len(sk['paras'])


def test_pick_respects_source_and_quiet_presets():
    for seed in range(5):
        sid, sk = rs.pick('tension', seed, ['MW', 'HY'])
        assert sid.split('-')[0] in {'MW', 'HY'}
        assert sum(1 for q in sk['paras'] if '!' in q.get('d', '')) <= 2


def test_v7_samples_follow_their_scores_and_fail_wrong_scores():
    pairs = {'V7_악보장면1_긴장.md': 'HY-0128', 'V7_악보장면2_고백.md': 'SD-0038'}
    for name, sid in pairs.items():
        text = (SAMPLES / name).read_text(encoding='utf-8')
        assert rs.fit_text(text, sid)['pass'], name
        other = [s for s in pairs.values() if s != sid][0]
        assert not rs.fit_text(text, other)['pass'], name


def test_voicecheck_score_flag_gates_verdict_and_replaces_preset_mix():
    text = (SAMPLES / 'V7_악보장면1_긴장.md').read_text(encoding='utf-8')
    saved = (vc.SCORE_ID, vc.PRESET)
    try:
        vc.PRESET = 'tension'
        vc.SCORE_ID = None
        _, issues_preset, _, _ = vc.score(text)
        vc.SCORE_ID = 'HY-0128'
        f, issues_score, _, v = vc.score(text)
        assert f['_rhythm']['pass'] and v.startswith('PASS')
        assert not any(str(i.get('key', '')).startswith('tension:') for i in issues_score)
        vc.SCORE_ID = 'SD-0038'
        _, _, _, v_wrong = vc.score(text)
        assert v_wrong.startswith('REWRITE')
    finally:
        vc.SCORE_ID, vc.PRESET = saved


def test_voice_card_names_rhythm_sources():
    out = subprocess.run([sys.executable, str(ROOT / 'tools/voice_seed.py'), '작품A'], capture_output=True, text=True).stdout
    m = re.search(r'\| 리듬 원천 \(v7\) \| ([A-Z, ]+) \|', out)
    assert m and set(x.strip() for x in m.group(1).split(',')) <= {'MW', 'HY', 'SD', 'CS'}
