-- 잠그기 1/2 — 로그인한 사람만 보이게
-- 전체를 SQL Editor 에 붙여넣고 Run. 여러 번 돌려도 안전하다.

-- 미니홈피에서 공개란 인터넷 전체가 아니라 이 집에 계정이 있는 사람이다.
create or replace function can_view(owner_id uuid, vis text) returns boolean
language sql stable security definer set search_path = public as $$
  select auth.uid() is not null and case vis
    when 'public'  then true
    when 'friends' then auth.uid() = owner_id or is_friend(auth.uid(), owner_id)
    else                auth.uid() = owner_id
  end;
$$;

-- ── 2. 프로필·방문수도 로그인해야 보인다 ──────────────────
drop policy if exists profiles_read on profiles;
create policy profiles_read on profiles for select
  using (auth.uid() is not null);

drop policy if exists visits_read on visits;
create policy visits_read on visits for select
  using (auth.uid() is not null);

