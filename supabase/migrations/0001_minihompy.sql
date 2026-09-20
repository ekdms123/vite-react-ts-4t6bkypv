-- 미니홈피 스키마 — 전체를 한 번에 실행한다.
--
-- 여러 번 실행해도 안전하다. 붙여넣다 잘렸거나 중간에 멈췄으면
-- 이 파일 전체를 다시 그대로 실행하면 된다.
--
-- 실행 후 아래로 확인:
--   select table_name from information_schema.tables
--   where table_schema = 'public' order by table_name;
--   → profiles, sections, entries, guestbook, friendships, visits 여섯 개가 나와야 한다.

create extension if not exists "pgcrypto";

-- 로그인 1개 = 미니홈피 1개
create table if not exists profiles (
  id          uuid primary key references auth.users on delete cascade,
  handle      text unique not null,          -- 주소: /@daeun
  title       text not null default '님의 미니홈피',
  tagline     text default '',               -- 좌측 페이지 한 줄
  mood        text default '',               -- TODAY IS.. 행복
  avatar_url  text,                          -- 프사(미니미)
  skin_key    text default 'sky',            -- 스킨 테마
  bgm_url     text,                          -- 쥬크박스 기본곡
  total_visits integer not null default 0,
  created_at  timestamptz not null default now()
);

-- 탭. 사용자가 직접 만들고 순서를 바꾼다.
-- kind가 렌더러를 고른다 → '일정'이면 kind='calendar'
create table if not exists sections (
  id          uuid primary key default gen_random_uuid(),
  owner       uuid not null references profiles on delete cascade,
  label       text not null,                 -- 탭에 보일 이름: "일정", "다이어리", 뭐든
  kind        text not null check (kind in
                ('diary','photo','board','calendar','todo','ledger','challenge',
                 'jukebox','guestbook','free')),
  position    integer not null default 0,
  visibility  text not null default 'public'
                check (visibility in ('public','friends','private')),
  created_at  timestamptz not null default now()
);
create index on sections (owner, position);

-- 글·사진·일정 전부 여기로. 컬럼은 kind별로 쓰는 것만 채운다.
create table if not exists entries (
  id          uuid primary key default gen_random_uuid(),
  section_id  uuid not null references sections on delete cascade,
  owner       uuid not null references profiles on delete cascade,
  title       text default '',
  body        text default '',
  images      text[] not null default '{}',  -- storage 경로들
  mood        text,                          -- diary
  weather     text,                          -- diary
  starts_at   timestamptz,                   -- calendar
  ends_at     timestamptz,                   -- calendar
  done        boolean not null default false, -- todo
  done_at     timestamptz,                   -- todo · challenge
  due_at      timestamptz,                   -- todo (마감)
  amount      numeric(12,0),                 -- ledger (원 단위)
  category    text,                          -- ledger · challenge
  -- 가계부는 '쓸 생각이던 돈'과 '실제로 쓴 돈'을 갈라야 회고가 된다.
  -- 한 칸에 섞으면 어디서 어긋났는지 물어볼 수가 없다.
  is_planned  boolean not null default false,
  meta        jsonb not null default '{}',   -- kind별 자유 필드
  visibility  text not null default 'public'
                check (visibility in ('public','friends','private')),
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create index on entries (section_id, created_at desc);
create index on entries (owner, starts_at);
create index on entries (owner, due_at) where done = false;

-- 방명록: 남의 집에 내가 쓴다
create table if not exists guestbook (
  id         uuid primary key default gen_random_uuid(),
  home       uuid not null references profiles on delete cascade,
  author     uuid not null references profiles on delete cascade,
  body       text not null,
  is_secret  boolean not null default false,
  created_at timestamptz not null default now()
);
create index on guestbook (home, created_at desc);

-- 일촌: 상호 수락
create table if not exists friendships (
  id             uuid primary key default gen_random_uuid(),
  requester      uuid not null references profiles on delete cascade,
  addressee      uuid not null references profiles on delete cascade,
  status         text not null default 'pending' check (status in ('pending','accepted')),
  requester_note text default '',            -- 일촌평
  addressee_note text default '',
  created_at     timestamptz not null default now(),
  accepted_at    timestamptz,
  check (requester <> addressee),
  unique (requester, addressee)
);

-- TODAY / TOTAL 카운터
create table if not exists visits (
  home  uuid not null references profiles on delete cascade,
  day   date not null default current_date,
  count integer not null default 0,
  primary key (home, day)
);

-- 일촌인가?
create or replace function is_friend(a uuid, b uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from friendships
    where status = 'accepted'
      and ((requester = a and addressee = b) or (requester = b and addressee = a))
  );
$$;

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

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users for each row execute function handle_new_user();

-- ── 방문 카운터 ──────────────────────────────────────────
-- 오늘치와 누적치를 한 번에 올린다. 남의 집도 올려야 하므로
-- security definer 로 두되, 올릴 수 있는 건 카운터뿐이다.
create or replace function bump_visit(home_id uuid) returns void
language plpgsql security definer set search_path = public as $$
begin
  insert into visits (home, day, count) values (home_id, current_date, 1)
    on conflict (home, day) do update set count = visits.count + 1;
  update profiles set total_visits = total_visits + 1 where id = home_id;
end;
$$;

grant execute on function bump_visit(uuid) to anon, authenticated;

-- ── 사진 저장소 ──────────────────────────────────────────
insert into storage.buckets (id, name, public)
values ('media', 'media', true)
on conflict (id) do nothing;

-- 경로 첫 칸이 uid다. 그래서 경로 모양이 곧 권한이 된다.
drop policy if exists "media read" on storage.objects;
create policy "media read" on storage.objects for select
  using (bucket_id = 'media');
drop policy if exists "media insert" on storage.objects;
create policy "media insert" on storage.objects for insert to authenticated
  with check (bucket_id = 'media' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "media update" on storage.objects;
create policy "media update" on storage.objects for update to authenticated
  using (bucket_id = 'media' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "media delete" on storage.objects;
create policy "media delete" on storage.objects for delete to authenticated
  using (bucket_id = 'media' and (storage.foldername(name))[1] = auth.uid()::text);
