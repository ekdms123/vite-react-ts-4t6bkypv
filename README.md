# 지개월 (JIGAEWOL)

사용자 > ZIP > 모델. 이 저장소로 여는 Claude Code 세션은 모든 메시지를 `jigaewol/` 안의 ZIP에 통과시킨다.

- `jigaewol/*.zip`: 지개월 ZIP. 새 버전은 이 파일만 바꾸면 된다.
- `.claude/settings.json`: 메시지를 보낼 때(UserPromptSubmit)와 답이 끝날 때(Stop) 훅을 부른다.
- `.claude/jigaewol_hook.py`: ZIP을 검증·활성화하고 ZIP 안의 `tools/jigaewol_chat_hook.py`를 실행한다.
- `.jigaewol_state/`: 세션별 원문·턴 기록 (git에 올리지 않음).

ChatGPT 등 훅이 없는 채팅은 ZIP을 첨부하고 ZIP 안의 `START_HERE.txt`대로 시작한다.
