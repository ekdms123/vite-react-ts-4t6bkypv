# 6단계로 나눠 설치하기

`0001_minihompy.sql` 한 장이 원본이다. 그걸 붙여넣다 3,500~4,300자 근처에서
두 번 잘렸고, 잘린 뒤쪽만 실행되면서 없는 테이블을 참조해 실패했다.
그래서 같은 내용을 문장 경계에서 1,800자 이하로 끊어 여기 뒀다.
함수 본문의 `$$` 블록 안에는 세미콜론이 있으므로 거기서는 끊지 않았다.

## 하는 법

`01.sql` → `06.sql` 순서대로, 각 파일 전체를 Supabase SQL Editor에 붙여넣고 Run.

순서가 중요하다. 뒤 단계는 앞 단계가 만든 테이블을 참조한다.
여러 번 돌려도 안전하니, 어디까지 했는지 모르겠으면 01부터 다시 하면 된다.

## 끝났는지 확인

```sql
select table_name from information_schema.tables
where table_schema = 'public' order by table_name;
```

`entries, friendships, guestbook, profiles, sections, visits` 여섯 개가 나오면 된다.

## 검증한 것

Postgres 16에 `../../test/scaffold.sql`로 Supabase 쪽 객체를 세운 뒤,
6단계를 순서대로 돌리고 한 번 더 돌렸다. 두 번 다 통과했고 결과는 원본 한 장과 같다:
테이블 6개, 정책 18개, 가입 트리거가 프로필 1개와 탭 9개를 깐다.
RLS도 원본과 같게 동작한다 — 남의 비공개·비밀글은 막히고, 일촌을 맺으면
`friends` 범위가 열리고, 남의 이름으로 쓰는 insert는 정책 위반으로 거부된다.
