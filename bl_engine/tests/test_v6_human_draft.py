"""목소리 층 v6 회귀 테스트: 빼기 퇴고 검사, 설계 티(S07~S09), 블로그 모드(B01~B03), T02 오탐 수정."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import voicecheck as vc
import subtract_check as sc

RAW = """블로그 시작함. 아니 시작했다고 하기도 애매한 게 예전에 만든 거 다시 연 거다. 비밀번호 찾는 데만 한참 걸렸다.
낭만부터 쓰려고 했는데 막혔다. 단풍 보러 간 적도 없다. 버스에서 머리 박았다. 그것도 낭만이라면 낭만인가.
이렇게 쓰고 보니까 둘이 아무 상관이 없다."""


def test_subtract_only_passes_deletions_and_particle_changes():
    final = """블로그 시작함. 예전에 만든 거 다시 연 거다. 비밀번호 찾는 데만 한참 걸렸음.
낭만부터 쓰려고 했는데 막혔다. 버스에서 머리 박았다."""
    r = sc.check(RAW, final)
    assert r['verdict'] == 'PASS' and r['added_words'] == 0


def test_subtract_only_flags_added_polish():
    final = """블로그 시작함. 결국 글은 마치 거울 같았다. 버스에서 머리 박았다."""
    r = sc.check(RAW, final)
    assert r['verdict'] == 'REWRITE'
    assert {'결국', '마치'} <= set(r['polish_added'])


def test_title_must_come_from_raw_words_except_keywords():
    assert sc.check_title(RAW, '매일 글쓰기 1일차, 버스에서 머리 박았다') == []
    assert sc.check_title(RAW, '매일 글쓰기 1일차, 가을이 내게 준 선물') != []


def test_hashtags_and_title_line_are_not_counted_as_added():
    final = '제목: 매일 글쓰기 1일차\n블로그 시작함.\n#매일글쓰기 #글쓰기챌린지'
    assert sc.check(RAW, final)['added_words'] == 0


def _ids(text, blog=False):
    saved = vc.BLOG_MODE
    vc.BLOG_MODE = blog
    try:
        f, issues, s, v = vc.score(text)
    finally:
        vc.BLOG_MODE = saved
    return {i.get('id') for i in issues}, v, f


DESIGNED = """처음부터 블로그를 할 생각은 없었다. 남이 안 보는 글은 쓰는 사람한테도 조금씩 거짓말을 시킨다. 그래서 꺼내 놓기로 했다.

가을의 낭만은 별게 아니다. 아침에 니트를 하나 더 걸치고 정류장에서 옷깃을 세우고 은행잎 밟는 소리를 듣고 캔커피를 산다. 바람이 목덜미로 들어온다. 걸음이 느려진다.

쓸쓸함은 같은 자리에서 온다. 저녁에는 니트가 모자라고 정류장에서 옷깃을 세워도 은행잎 밟는 소리가 혼자 크고 캔커피도 식는다. 바람이 목덜미로 들어온다. 걸음이 느려진다.

다 쓰고 보니 결국 같은 니트 얘기였다. 가을 감성 글귀를 검색하면 하늘이 높다는 말만 나온다."""


def test_design_tells_fire_on_designed_draft():
    ids, v, _ = _ids(DESIGNED)
    assert {'S07', 'S08', 'S09'} <= ids


def test_blog_mode_adds_register_checks_and_ignores_novel_discriminator():
    ids, v, f = _ids(DESIGNED, blog=True)
    assert {'B02', 'B03'} <= ids
    # 블로그 모드 판정은 패턴 점수만으로 정해진다(판별기는 BL 소설 기준이라 참고만)
    saved = vc.BLOG_MODE
    vc.BLOG_MODE = True
    try:
        _, _, s, verdict = vc.score('나는 오늘 밥을 먹었다. 맛있었다. 버스를 탔다. 집에 왔다. ' * 20)
    finally:
        vc.BLOG_MODE = saved
    assert verdict.startswith('PASS') == (s <= vc.TARGETS['pass_threshold'])


def test_t02_does_not_flag_literal_seems():
    ids, _, _ = _ids('네 번째 갔을 때 직원분이 나를 알아보는 것 같았다. 서로 아무 말 안 했다.')
    assert 'T02' not in ids
    ids, _, _ = _ids('그는 세무서 직원처럼 영수증을 셌다. 나는 웃었다.')
    assert 'T02' in ids


def test_protocol_docs_exist_and_are_linked():
    proto = (ROOT / 'runtime/HUMAN_DRAFT_PROTOCOL.md').read_text(encoding='utf-8')
    assert 'subtract_check' in proto and '빼기' in proto
    assert (ROOT / 'runtime/LIFE_CARD_TEMPLATE.md').is_file()
    assert 'HUMAN_DRAFT_PROTOCOL' in (ROOT / 'runtime/BL_WRITER_RUNTIME.md').read_text(encoding='utf-8')
    assert 'HUMAN_DRAFT_PROTOCOL' in (ROOT / 'README.md').read_text(encoding='utf-8')
