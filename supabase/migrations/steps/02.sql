-- 미니홈피 설치 — 2단계 / 총 6단계
-- 이 파일 전체를 SQL Editor에 붙여넣고 Run.
-- 순서대로 하고, 여러 번 돌려도 안전하다.

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
