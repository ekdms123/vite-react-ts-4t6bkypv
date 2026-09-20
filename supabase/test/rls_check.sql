-- RLS 검사. 스키마를 고칠 때마다 돌린다.
--
-- 로컬 Postgres에서 supabase/test/scaffold.sql → 0001_minihompy.sql → 이 파일 순으로 실행한다.
-- superuser는 RLS를 통과하므로 반드시 authenticated 역할로 접속해서 돌려야 한다.
-- 한 번 이 검사를 superuser로 돌렸다가 전부 통과하는 착시를 봤다.
--
-- 기대값이 틀리면 즉시 멈춘다.

\set ON_ERROR_STOP on

do $$
declare
  a uuid; b uuid; n int;
begin
  select id into a from profiles order by created_at asc  limit 1;
  select id into b from profiles order by created_at desc limit 1;
  if a = b then
    raise exception '두 사람이 같은 id다. created_at이 같으면 정렬이 같은 행을 집는다';
  end if;
  raise notice 'A=% B=%', a, b;
end $$;

-- 아래는 authenticated 역할 + request.jwt.claim.sub = B 로 실행한다.
-- 1) 남의 비공개는 안 보인다
select case when count(*) = 0 then 'PASS' else 'FAIL' end as "1 비공개 차단"
from sections where visibility = 'private' and owner <> auth.uid();

-- 2) 남의 공개는 보인다
select case when count(*) > 0 then 'PASS' else 'FAIL' end as "2 공개 열람"
from sections where visibility = 'public' and owner <> auth.uid();

-- 3) 남의 것은 못 지운다
with gone as (delete from sections where owner <> auth.uid() returning 1)
select case when count(*) = 0 then 'PASS' else 'FAIL' end as "3 삭제 차단" from gone;

-- 4) 일촌이면 friends 범위가 열린다
select case when count(*) > 0 then 'PASS' else 'FAIL' end as "4 일촌 열람"
from sections s where s.visibility = 'friends' and is_friend(auth.uid(), s.owner);

-- 5) 비밀 방명록은 당사자만
select case when count(*) = 0 then 'PASS' else 'FAIL' end as "5 비밀글 차단"
from guestbook where is_secret and home <> auth.uid() and author <> auth.uid();
