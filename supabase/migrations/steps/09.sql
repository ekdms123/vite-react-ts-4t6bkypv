-- 업그레이드 — 앨범 · 사진 댓글 · 수입지출
-- 전체를 SQL Editor 에 붙여넣고 Run.

-- 앨범 · 댓글 · 수입지출
--
-- 이 파일 전체를 SQL Editor에 붙여넣고 Run. 여러 번 돌려도 안전하다.

-- ── 사진 댓글 ────────────────────────────────────────────
-- 싸이월드에서 사진첩이 살아 있던 이유는 사진이 아니라 그 아래 달린
-- 댓글이었다. 댓글은 글과 수명이 다르므로 따로 둔다.
create table if not exists comments (
  id         uuid primary key default gen_random_uuid(),
  entry_id   uuid not null references entries on delete cascade,
  author     uuid not null references profiles on delete cascade,
  body       text not null,
  created_at timestamptz not null default now()
);
create index if not exists comments_entry_idx on comments (entry_id, created_at);
alter table comments enable row level security;

-- 댓글은 그 사진을 볼 수 있는 사람만 읽고 쓴다.
-- 사진이 안 보이는데 댓글만 보이면 내용이 새어 나간다.
drop policy if exists comments_read on comments;
create policy comments_read on comments for select using (
  exists (select 1 from entries e
          where e.id = entry_id and can_view(e.owner, e.visibility))
);
drop policy if exists comments_insert on comments;
create policy comments_insert on comments for insert with check (
  auth.uid() = author and exists (
    select 1 from entries e
    where e.id = entry_id and can_view(e.owner, e.visibility))
);
-- 쓴 사람과 집주인이 지울 수 있다.
drop policy if exists comments_delete on comments;
create policy comments_delete on comments for delete using (
  auth.uid() = author
  or exists (select 1 from entries e where e.id = entry_id and e.owner = auth.uid())
);

-- ── 사진 페이지 꾸미기 ───────────────────────────────────
-- 사진 한 장이 곧 한 페이지가 되도록 배경·글귀를 따로 갖는다.
alter table entries add column if not exists decor jsonb not null default '{}';

-- ── 가계부 ───────────────────────────────────────────────
-- 들어온 돈과 나간 돈을 한 부호로 섞으면 합계가 아무것도 말해주지 않는다.
alter table entries add column if not exists is_income boolean not null default false;

-- ── 앨범 ─────────────────────────────────────────────────
-- 사진첩의 폴더. 이미 있는 category 칸을 앨범 이름으로 쓴다.
-- 표가 하나 더 늘지 않고, 기존 사진은 '기본' 앨범으로 모인다.
create index if not exists entries_album_idx on entries (section_id, category);
