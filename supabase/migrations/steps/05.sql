-- 미니홈피 설치 — 5단계 / 총 6단계
-- 이 파일 전체를 SQL Editor에 붙여넣고 Run.
-- 순서대로 하고, 여러 번 돌려도 안전하다.

create policy guestbook_read on guestbook for select
  using (not is_secret or auth.uid() = home or auth.uid() = author);
drop policy if exists guestbook_insert on guestbook;
create policy guestbook_insert on guestbook for insert with check (auth.uid() = author);
drop policy if exists guestbook_delete on guestbook;
create policy guestbook_delete on guestbook for delete
  using (auth.uid() = author or auth.uid() = home);

-- 일촌: 당사자만 (R5)
drop policy if exists friendships_read on friendships;
create policy friendships_read on friendships for select
  using (auth.uid() in (requester, addressee));
drop policy if exists friendships_insert on friendships;
create policy friendships_insert on friendships for insert
  with check (auth.uid() = requester);
drop policy if exists friendships_update on friendships;
create policy friendships_update on friendships for update
  using (auth.uid() in (requester, addressee));

drop policy if exists visits_read on visits;
create policy visits_read on visits for select using (true);

-- 가입하면 미니홈피가 자동으로 생긴다: 프로필 + 기본 탭 6개
create or replace function handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare new_handle text;
begin
  new_handle := 'u' || substr(replace(new.id::text, '-', ''), 1, 8);
  insert into profiles (id, handle) values (new.id, new_handle);
  insert into sections (owner, label, kind, position) values
    (new.id, '오늘',     'todo',      1),
    (new.id, '달력',     'calendar',  2),
    (new.id, '다이어리', 'diary',     3),
    (new.id, '사진첩',   'photo',     4),
    (new.id, '가계부',   'ledger',    5),
    (new.id, '챌린지',   'challenge', 6),
    (new.id, '쥬크박스', 'jukebox',   7),
    (new.id, '보관함',   'free',      8),
    (new.id, '방명록',   'guestbook', 9);
  return new;
end;
$$;
