-- 미니홈피 설치 — 1단계 / 총 6단계
-- 이 파일 전체를 SQL Editor에 붙여넣고 Run.
-- 순서대로 하고, 여러 번 돌려도 안전하다.

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
