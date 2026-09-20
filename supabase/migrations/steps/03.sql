-- 미니홈피 설치 — 3단계 / 총 6단계
-- 이 파일 전체를 SQL Editor에 붙여넣고 Run.
-- 순서대로 하고, 여러 번 돌려도 안전하다.

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
