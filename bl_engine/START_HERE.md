# BL VOICE ENGINE 6.0.0 — 먼저 읽기 (목소리 층 v7)

**리듬을 규칙으로 만들지 않고 사람 원작에서 빌리는 판이다.**

| 바뀐 것 | 내용 |
|---|---|
| **리듬 악보** `tools/rhythm_score.py` + `voice/rhythm_scores.json` | BL 원작 4종 덩어리 530개의 골격(문단 종류·문장 길이·종결·장치 위치). 단어 없음. `pick --preset tension --src MW,HY`로 뽑아 그 위에 쓰고, `fit`으로 따랐는지 잰다 |
| `voicecheck --score 악보ID` | 악보 맞춤(≥0.645)을 판정에 넣고, 엔진 프리셋 믹스 대신 사람 악보를 기준으로 삼는다 |
| 판별기 적대적 재학습 | v5에서 판별기를 통과한 장면을 AI 쪽에 넣어 다시 학습(LOGO AUC 0.971). 판별기 특징을 알고 쓴 글이 판별기를 넘는다는 것을 확인하고 막았다 |
| 손버릇 카드: 리듬 원천 | 작품마다 원작 1~2편만 리듬 원천으로 쓴다. 작품 안에서는 일관되고, 작품끼리는 다르다 |
| 새 장면 2개 | 악보 위에 쓴 긴장·고백 장면: 악보 맞춤 0.977·0.967, 재학습 판별기 0.52·0.59 (이전 엔진 출력 0.01~0.03) |

정직한 한계: 리듬 근접도 자체는 AI를 가르지 못했다(AI 글도 어떤 사람 악보에는 가깝다). 악보는 판정 도구가 아니라 집필 틀이다. 블라인드 판별자 시험은 아직이다. 근거: `verify/V7_RHYTHM_REPORT.md`.

```
python tools/voice_seed.py "제목" > PROJECT_VOICE_CARD.md
python tools/rhythm_score.py pick --preset confession --src SD
python tools/voicecheck.py 원고.md --score SD-0038
```

---

# (이력) BL VOICE ENGINE 5.0.0 (목소리 층 v6)

**쓰는 방식을 뒤집은 판이다.** 4.0.0까지는 '사람 같은 장치를 더하고 걸린 문장을 더 잘 고치는' 엔진이었다. 그 방식으로 쓴 블로그 초안은 검사기 0점·판별기 0.986으로 통과했지만, 사람이 읽자마자 "AI가 잘 쓴 느낌, 잘 쓰려고 노력한 느낌"이라고 잡았다. 원인은 단어가 아니라 퇴고 때 더해진 설계(교훈 문장, 회수 요약, 대구로 맞춘 문단, 문단마다 펀치, 검색어 끼워 넣기)였다.

| 바뀐 것 | 내용 |
|---|---|
| `runtime/HUMAN_DRAFT_PROTOCOL.md` | 말로 쏟은 초고 → **빼기만 하는 퇴고**. 제목도 초고 속 말로. 논픽션 디테일은 실화 카드에서만 |
| `tools/subtract_check.py` | 완성본이 초고에서 빼기만 했는지 검증(더한 말 8% 이하, 덧칠 단어 0, 제목 단어 출처) |
| `voicecheck` 설계 티 S07~S09 | 교훈 문장·회수 요약·거울 구조. BL 원작 덩어리에서 0.2%·0.2%·1% 미만으로만 나오는 것 |
| `voicecheck --blog` | 블로그·에세이 모드: B01 문어체 종결, B02 검색어 끼워 넣기 문장, B03 계절 소품 클리셰(잠정 목록). BL 소설 기준 판별기는 참고만 |
| `runtime/LIFE_CARD_TEMPLATE.md` | 블로그 실화 카드. 생활 디테일은 여기서만 가져오고 지어내지 않는다 |
| T02 오탐 수정 | "직원분이 나를 알아보는 것 같았다" 같은 문장을 직유로 잡던 것 수정 |

같은 블로그 1일차: v5 방식 초안 → v6 검사기 **28점 REWRITE**(S07·S08·S09·B02·B03). v6 방식 완성본 → **0점 PASS**, 빼기 검사 더한 말 0어절.

```
python tools/subtract_check.py 초고.md 완성.md
python tools/voicecheck.py 완성.md --blog        # BL 원고는 --blog 없이
```

---

# (이력) BL VOICE ENGINE 4.0.0

3.2.1의 목소리 층을 **원작 실측으로 다시 맞춘 판**(목소리 층 v5)이다. 장면 권한·지식 경계·검증 장부(stateful_author)는 그대로다.

## 무엇이 바뀌었나 (자세한 근거: `verify/V5_CALIBRATION_REPORT.md`)

| 바뀐 것 | 이유 |
|---|---|
| **판별기** `tools/discriminator.py` + `voice/discriminator_model.json` | BL 원작 4종 vs AI 글로 학습한 추상 문체 모델. 떼어 둔 작품으로 시험해 AUC 0.986. 덩어리마다 P(사람 원작)와 'AI 쪽으로 미는 특징 + 고치는 법'을 낸다. 표준 라이브러리만 쓴다 |
| `voicecheck.py` v5 | 통과 = 패턴 점수 ≤15 **그리고** P_HUMAN ≥0.5. 덩어리 최소치 강제 폐지(→ `--series`), 원작에서 역효과였던 규칙 정리, 점수가 설치 환경에 따라 바뀌던 버그 수정 |
| 성능 | 떼어 둔 원작 BL 통과율 57% → **92%**, AI 덩어리 통과율 → **0%(0/21)**. v3는 엔진 샘플 V1~V3를 통과시켰고 v5는 셋 다 REWRITE |
| **장치 지문** `voice_seed.py` | 사람 작가는 장치 몇 개만 자기 것으로 쥔다('!!' 등장률이 작품마다 0%~73%). 카드가 작품마다 장치를 켬/끔으로 뽑고, `--series`의 [분포]가 고르게 깔린 장치를 잡는다 |
| **문체 = BL만** (바이블 §(f)) | 비BL·빙의글은 감정선·유머·재치 '구조'만. 비BL이 맡던 욕 박자·고풍 부사·대시·말투는 BL 주인에게 넘기거나 삭제 |
| 리듬 재보정 | 단문 연타는 AI 쪽이었다(서술문 평균 원작 30자 vs AI 20자, 대사 25 vs 13). 숫자·단위 정밀 추적은 AI 지문(×4.7) |
| banlist K01~K07 | slop-forensics 방식을 한국어로 이식해 찾은 몸동작 지문 클리셰(굳었다·멈췄다·~웃음이었다·바라보았다·내려놓았다·너머로·대답하지 않았다·숨 들이켜기) |
| 오픈소스 실제 설치·이식 | `vendor/`(MIT 6종), 원장 `docs/DONOR_LEDGER.md`. 영어 검사기가 한국어 AI 글을 '사람'으로 판정하는 것까지 실측해 기록 |
| 블라인드 관문 | `verify/BLIND_JUDGE_PROTOCOL.md` (EQ-Bench 쌍대 비교 구조를 한국어 BL용으로) |

## 쓰는 법 (모바일 채팅창 기준)

1. 이 zip을 올리고 "runtime/BL_WRITER_RUNTIME.md의 v5 실행 순서대로 써 줘"라고 한다.
2. 작품 시작 때 한 번: `python tools/voice_seed.py "작품 제목" > PROJECT_VOICE_CARD.md`
3. 덩어리마다: `python tools/voicecheck.py a.md b.md c.md --rank --preset comedy --card PROJECT_VOICE_CARD.md` → 1등만 단독 리포트 → [판별] 상위 3개와 [금지]만 고친다
4. 화가 쌓이면: `python tools/voicecheck.py 1화.md 2화.md 3화.md --series`
5. 원작·AI 글이 더 생기면 재학습: `python tools/train_discriminator.py --human 원작폴더 --ai AI폴더` (numpy·scikit-learn), 검사기 재평가: `python tools/eval_checker.py ...`
6. 새 AI 버릇 찾기: `python tools/slop_forensics_ko.py --ai AI폴더 --human 원작폴더`

코드를 못 돌리면 BL_WRITER_RUNTIME의 'v5 수동 8문항'으로 대신한다.

## 정직한 현재 상태

- 판별기와 검사기는 '원작 4종의 추상 분포에 가까운가'를 잰다. v5 지침으로 새로 쓴 시험 장면 둘은 P_HUMAN 0.98로 통과했지만, 판별기 특징을 아는 상태에서 쓴 글이다.
- **블라인드 판별자 재시험(4라운드)은 아직 하지 않았다.** 3라운드까지는 판별자 셋이 엔진 글을 모두 AI로 판정했다. 상태는 ASSURANCE_NOT_MET(`verify/CLAIM_LEDGER.json`의 V5_HUMAN_INDISTINGUISHABLE).
- AI 표본은 21덩어리라 K01~K07과 판별기 가중치는 잠정치다.
- 원작 문장·원작 인물명은 들어 있지 않다. 판별기 모델에는 특징 통계와 가중치만 있다(테스트로 확인).

---

# (이력) BL VOICE ENGINE 3.2.1

「우연이 너무 길었지」(3.1.0a2) 위에 **BL 전용 목소리 층**을 얹은 판이다. 원래 엔진의 장면 권한·지식 경계·검증 장부는 그대로 두었다.

## 무엇이 들어갔나

| 위치 | 내용 |
|---|---|
| `voice/VOICE_BIBLE.md` | 합성 작가 GJ: 차원별 담당(부위별 이식), 절대 규칙 10, 장면 프리셋 5종 |
| `voice/BL_LAYER.md` | 지칭어 사다리, 반말·존댓말 전환, 공·수 시점 비대칭, 스킨십·질투·고백 처리 |
| `voice/MICRO_MOVES.md` | 기술 50여 개(지어낸 예문, 남용 한도) |
| `voice/ANTI_AI_PLAYBOOK.md` | 검사기 항목별 고쳐 쓰기 작업표 |
| `voice/BL_VOCAB.md` / `bl_vocab.json` | 원작 5종 실측 단어장(참고용): 피할 단어→대체어, 태도 부사, 지칭어, 관용구, 의태어, BL 키워드 |
| `voice/AI_HUMAN_CONTRAST.md` | Claude 기본 출력 대 사람 원작 35개 대조(실측 배율) |
| `voice/style_targets.json` / `banlist.json` / `MEASURED_BANDS.json` | 원작 실측 수치 범위, 금지 패턴 50여 개, 원 측정값 |
| `tools/voicecheck.py` | 검사기. 단일 검사, 후보 순위(--rank), 프리셋(--preset), 연재 버릇(--series), 손버릇 카드(--card) |
| `tools/voice_seed.py` | 작품별 손버릇 카드 생성기 |
| `runtime/BL_WRITER_RUNTIME.md` | 집필 순서(후보 3개 → 검사 → 걸린 곳만 고치기) |
| `verify/BL_BLIND_TEST_RESULTS.json` | 블라인드 판별 3라운드 결과(정직 기록) |

## 쓰는 법 (모바일 채팅창 기준)

1. 이 zip을 채팅에 올리고 "runtime/BL_WRITER_RUNTIME.md대로 써 줘"라고 한다.
2. 작품 시작 때 한 번: `python tools/voice_seed.py "작품 제목"`
3. 덩어리마다: `python tools/voicecheck.py 후보A.md 후보B.md 후보C.md --rank --preset comedy --card PROJECT_VOICE_CARD.md`
4. 화가 쌓이면: `python tools/voicecheck.py 1화.md 2화.md 3화.md --series`
5. 단어 고를 때: `python tools/voicecheck.py 원고.md --vocab` (참고 리포트, 점수 무관)

코드 실행이 안 되면 BL_WRITER_RUNTIME §3의 수동 12문항으로 대신한다.

## 정직한 현재 상태

- 검사기는 원작 구간(중앙값 4~27점)과 Claude 기본 장면(중앙값 72.5점, 최저 38점)을 겹침 없이 가른다.
- 엔진으로 쓴 장면은 검사기 0~8점까지 내려간다.
- **그러나 블라인드 판별자(LLM 3명)는 3라운드 모두 엔진 글을 AI로 판정했다.** AI 확률은 기본 글 약 92 → 엔진 글 약 75로 내려갔지만 사람 원작(약 8)과는 아직 거리가 있다. 남은 판별 근거와 시험의 한계는 `verify/BL_BLIND_TEST_RESULTS.json`에 있다.
- 원작 문장·원작 인물명은 들어 있지 않다. 원작에서 가져온 것은 수치와 장치 설명뿐이다.

---

# Start Here — Grounded Synthetic Creative Cognition Runtime 3.1.0a2

This release implements the v0.2 executable-contract redesign.

For prose realization, use `runtime/WRITER_RUNTIME.md` and the positive-constructed packet schema in `runtime/WRITER_PACKET_SCHEMA.json`. The writer does not receive raw canonical state, reader answers, hidden plans, or objective affordances that the focal character cannot perceive.

For integrity, the official path is:

`prepare_scene()` -> external writer/model -> `verify_proposal()` -> typed `StateDelta` -> `commit_verified()`.

Do not use the legacy `qualify_proposal()` path; it is disabled by design.

Implementation truth is recorded in `verify/EXECUTION_LEDGER.json`. Claim limits are recorded in `verify/CLAIM_LEDGER.json`. Fresh structural evidence is recorded in `verify/V02_VERIFICATION_BUNDLE.json` and tied to code/schema/ledger/version fingerprints.

`verify/BENCHMARK_PROTOCOL.json` defines the not-yet-run controlled literary comparison. Literary superiority remains `ASSURANCE_NOT_MET` until that external evaluation exists.
