---
type: usagi-bridge-contract
status: active-transport
---
# USAGI ↔ Obsidian Bridge Contract

이 vault의 Markdown 파일은 Obsidian과 USAGI가 함께 읽고 쓸 수 있는 장기 지식 저장소 후보입니다.

## Initial safety rules
- `.obsidian` 설정은 명시적 요청 없이 수정하지 않는다.
- 삭제/이동은 현재 사용자 요청이 명시적일 때만 한다.
- 쓰기 전 현재 파일 상태를 읽고, 쓰기 후 read-back으로 검증한다.
- GitHub transport의 성공과 실제 Obsidian 앱 동기화 성공을 구분한다.
- repo가 public인 동안에는 민감정보/개인정보를 쓰지 않는다.
