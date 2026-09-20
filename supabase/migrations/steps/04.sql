-- 미니홈피 설치 — 4단계 / 총 6단계
-- 이 파일 전체를 SQL Editor에 붙여넣고 Run.
-- 순서대로 하고, 여러 번 돌려도 안전하다.

-- 이 뷰어가 이 visibility를 볼 수 있나?
create or replace function can_view(owner_id uuid, vis text) returns boolean
language sql stable security definer set search_path = public as $$
  select case vis
    when 'public'  then true
    when 'friends' then auth.uid() = owner_id or is_friend(auth.uid(), owner_id)
    else                auth.uid() = owner_id
  end;
$$;

alter table profiles    enable row level security;
alter table sections    enable row level security;
alter table entries     enable row level security;
alter table guestbook   enable row level security;
alter table friendships enable row level security;
alter table visits      enable row level security;

-- 프로필은 누구나 보되, 고치는 건 본인만 (R8)
drop policy if exists profiles_read   on profiles;
create policy profiles_read   on profiles for select using (true);
drop policy if exists profiles_insert on profiles;
create policy profiles_insert on profiles for insert with check (auth.uid() = id);
drop policy if exists profiles_update on profiles;
create policy profiles_update on profiles for update using (auth.uid() = id);

-- 탭/글: 공개범위대로 읽고, 쓰는 건 주인만 (R2)
drop policy if exists sections_read on sections;
create policy sections_read on sections for select using (can_view(owner, visibility));
drop policy if exists sections_write on sections;
create policy sections_write on sections for all
  using (auth.uid() = owner) with check (auth.uid() = owner);

drop policy if exists entries_read on entries;
create policy entries_read on entries for select using (can_view(owner, visibility));
drop policy if exists entries_write on entries;
create policy entries_write on entries for all
  using (auth.uid() = owner) with check (auth.uid() = owner);

-- 방명록: 집주인과 글쓴이만 비밀글을 본다
drop policy if exists guestbook_read on guestbook;
