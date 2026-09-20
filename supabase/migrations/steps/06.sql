-- 미니홈피 설치 — 6단계 / 총 6단계
-- 이 파일 전체를 SQL Editor에 붙여넣고 Run.
-- 순서대로 하고, 여러 번 돌려도 안전하다.

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
