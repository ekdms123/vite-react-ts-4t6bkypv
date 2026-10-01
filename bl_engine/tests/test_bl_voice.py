import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import voicecheck as vc

AI_LIKE = """새벽 두 시의 편의점은 생각보다 조용했다.

그는 대답 대신 고개를 끄덕였다. 귀 끝이 붉어졌다. 아주 잠깐, 숨이 막혔다.

삼 년 동안 한 번도 연락하지 않았다. 그건 무관심이 아니었다. 그래서 더 아팠다.

둘 다 아무 말도 하지 않았다. 창밖에는 비가 여전히 그치지 않았다.

손에 쥔 캔커피가 아직 따뜻했다."""

HUMAN_LIKE = """“너 그거 또 내 샴푸지.”

세탁기 위에 걸터앉은 놈이 거품을 불었다. 미친놈. 저걸 어디서 배웠냐. 유치원? 나는 수건을 집어 던졌고 놈은 그걸 얼굴로 받았다. 안 피한다. 원래 안 피하는 놈이다. 맞고 나서 웃는다. 그게 더 열받는다는 걸 아는 얼굴로, 젖은 수건을 머리에 얹은 채 다리를 까딱거리며 반값 스티커가 붙은 삼각김밥 봉지를 뜯는 손이 영 바빴다.

“먹을래?”

참치마요. 내 거다."""


def test_ai_like_scores_worse_than_human_like():
    _, _, s_ai, _ = vc.score(AI_LIKE)
    _, _, s_h, _ = vc.score(HUMAN_LIKE)
    assert s_ai > s_h + 20


def test_measured_bans_fire():
    _, issues, _, _ = vc.score(AI_LIKE)
    ids = {i.get('id') for i in issues}
    assert {'M02', 'M04', 'M11', 'C01'} <= ids


def test_targets_and_banlist_are_valid_json_and_regex():
    import re
    t = json.loads((ROOT / 'voice/style_targets.json').read_text(encoding='utf-8'))
    b = json.loads((ROOT / 'voice/banlist.json').read_text(encoding='utf-8'))
    assert set(t['presets']) == {'comedy', 'tension', 'confession', 'fight', 'tragedy'}
    for p in b['patterns']:
        re.compile(p['regex'])


def test_voice_seed_is_deterministic_and_differs_by_title():
    a = subprocess.run([sys.executable, str(ROOT / 'tools/voice_seed.py'), '작품A'], capture_output=True, text=True).stdout
    a2 = subprocess.run([sys.executable, str(ROOT / 'tools/voice_seed.py'), '작품A'], capture_output=True, text=True).stdout
    b = subprocess.run([sys.executable, str(ROOT / 'tools/voice_seed.py'), '작품B'], capture_output=True, text=True).stdout
    assert a == a2 and a != b and '고풍 부사' in a


def test_bl_vocab_reference_is_present_and_consistent():
    v = json.loads((ROOT / 'voice/bl_vocab.json').read_text(encoding='utf-8'))
    md = (ROOT / 'voice/BL_VOCAB.md').read_text(encoding='utf-8')
    assert '참고용' in v['meta']['rule'] and '끼워 넣지' in v['meta']['rule']
    for w, *_ in v['swaps']:
        assert w in md
    ids = {p['id'] for p in json.loads((ROOT / 'voice/banlist.json').read_text(encoding='utf-8'))['patterns']}
    assert {'V01', 'V02', 'V03'} <= ids
