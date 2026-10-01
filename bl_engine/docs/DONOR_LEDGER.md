# DONOR LEDGER — 외부 오픈소스·자료 이식 원장 (v5, 2026-10-01)

각 항목을 `받음 / 설치 / 실행 / 결과 / 엔진에 들어간 것`으로 나눈다. 문서를 읽은 것을 실행했다고 적지 않는다.
커밋 해시는 `vendor/UPSTREAM_COMMITS.md`.

## GitHub 오픈소스

| 저장소 | 라이선스 | 설치 | 실행 결과 | 엔진에 들어간 것 |
|---|---|---|---|---|
| conorbronsdon/avoid-ai-writing | MIT | `npm install -g` (CLI `avoid-ai-writing`), Claude 스킬 설치 | 영어 AI 문장 25점(탐지). **엔진 v3로 쓴 한국어 Claude 기본 장면은 0점·HUMAN_ONLY** — 영어 패턴 검사기는 한국어 AI 티를 보지 못한다 | `vendor/avoid-ai-writing/`(스킬·탐지기·CLI, node만 있으면 `node vendor/avoid-ai-writing/bin/avoid-ai-writing.js 파일` 실행). P0~P2 심각도·iterate-to-convergence 구조를 v5 루프에 반영 |
| blader/humanizer | MIT | Claude 스킬 설치 | 스킬 등록 확인 | `vendor/humanizer/`. "소설은 지어낸 디테일이 과제라 예외" 원칙, 사실 추가 금지 원칙 |
| kjmagnan1s/anti-slop | MIT | Claude 스킬 설치 | 스킬 등록 확인 | `vendor/anti-slop/`. **protect-list** 개념 → v5 [과잉/이탈] 가드(원작 범위 밖으로 고치지 않기)와 '작가 원칙(house_rule)' 분리 |
| aplaceforallmystuff/the-antislop | MIT | Claude 스킬 설치 | 스킬 등록 확인 | `vendor/the-antislop/`. Horoscope Test("누구나 누구에게나 쓸 수 있는 문장인가") → 장면 카드 '살아 있는 문제' 점검 |
| adewale/anti-slop-writing | MIT | Claude 스킬 설치 | 스킬 등록 확인 | `vendor/anti-slop-writing/`. "날카로운 디테일 > 부풀린 의미", 결론을 구체물로 되돌리기 → 장면 끝 규칙과 합치 |
| sam-paech/slop-forensics | MIT | pip 의존성 설치, 모듈 임포트 | 원본 토큰화가 `[a-zA-Z']+`라서 한국어를 0개로 센다. 과대출현 함수만 한국어 어절로 실행 → K01~K07 발견 | `tools/slop_forensics_ko.py`(함수 이식, 저작권 표기), `vendor/slop-forensics/` |
| sam-paech/antislop-sampler | Apache-2.0 | 받음 | 로컬 모델 로짓(transformers/vLLM)에 백트래킹을 거는 방식. Claude 채팅에서는 로짓 접근이 없어 실행 불가 | 개념만: '금지 구문이 나오면 그 지점부터 다시 쓴다' → v5 루프의 '걸린 문장만 고치기' |
| sam-paech/auto-antislop | 라이선스 파일 없음 | 받음 | 생성→과대출현 분석→금지→재생성 반복(DPO 학습 포함). 학습 부분은 Claude에서 불가 | 반복 구조만: BLIND_JUDGE_PROTOCOL의 '판별 근거 → banlist·특징 후보' 기록 |
| EQ-bench/creative-writing-bench | 라이선스 파일 없음 | 받음, 심사 기준·쌍대 프롬프트 열람 | — | 코드·프롬프트 문장은 넣지 않음. 쌍대 비교·무승부 금지·차이 크기(+~+++++)·'장식 과잉' 기준 구조를 `verify/BLIND_JUDGE_PROTOCOL.md`에 한국어로 새로 씀 |
| EdwardAThomson/NovelWriter | 라이선스 파일 없음 | 받음 | 실행에는 LLM API 키 필요. 검수는 길이·문단·키워드 휴리스틱 수준 | 단계 분리(세계관→개요→장면→원고→검수) 원칙만. 이 엔진의 stateful_author가 이미 더 강한 구조를 가짐 |

## Notion DAEUN VAULT

| 페이지 | 반영 |
|---|---|
| conorbronsdon/avoid-ai-writing (SRC-658) | 위 표. Notion 메모대로 "영어 기준이라 한국어 검수 규칙의 구조 참고용"이 실측으로 확인됨 |
| AI NovelWriter (SRC-66) | 위 표 |
| 창작 프롬프트 8칸 구조 (SRC-53) | 장면 카드를 고정값/가변값으로 나눔(BL_WRITER_RUNTIME v5) |
| RIKU (SRC-137) | AI 역할 = 정리·후보·첫 독자, 대필기 아님(BL_WRITER_RUNTIME v5) |
| ❤️ (JIGAEWOL 작업 원장) | 'installed / connected / callable / executed / successful' 구분 → 이 원장의 열 구성. `prose_style_auditor`의 '창작 모드에서는 낯선 표현을 벌점 주지 않는다' → 판별기가 어휘 내용을 보지 않는 설계 |

## Google Drive 「글집」

| 파일 | 사용 |
|---|---|
| 우리철수.txt, 세디백 첫병.txt, [유수]마왕.txt, [유수]홍염의연인.txt | BL 원작. 판별기 학습·장치 분포·밴드 재보정. 해시가 author_analysis/SOURCE_REGISTRY.json과 일치(세디·마왕·홍염). 원문은 엔진에 넣지 않았다 |
| 영화학도 개복치.txt.docx | 빙의글(비BL). 작가 원칙에 따라 문체 학습에서 제외. 감정선·유머·재치 '구조'만 기존 바이블 담당으로 남김 |
