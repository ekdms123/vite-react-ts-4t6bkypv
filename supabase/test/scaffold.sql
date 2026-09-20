-- Supabase가 미리 깔아두는 것 중 이 스키마가 기대는 것만 최소로 흉내 낸다.
-- 로컬에서 마이그레이션을 검증할 때만 쓴다. 실제 Supabase에는 넣지 않는다.

create role anon;
create role authenticated login nosuperuser nobypassrls;
create schema if not exists auth;
create schema if not exists storage;

create table auth.users (id uuid primary key default gen_random_uuid());

create or replace function auth.uid() returns uuid
language sql stable as $$
  select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
$$;

create table storage.buckets (
  id text primary key, name text not null, public boolean not null default false);
create table storage.objects (
  id uuid primary key default gen_random_uuid(),
  bucket_id text references storage.buckets, name text);
alter table storage.objects enable row level security;

create or replace function storage.foldername(name text) returns text[]
language sql immutable as $$ select string_to_array(name, '/') $$;

grant usage on schema public to anon, authenticated;

-- 마이그레이션을 돌린 뒤에 아래를 실행해 권한을 준다.
--   grant all on all tables in schema public to anon, authenticated;
--   grant execute on all functions in schema public to anon, authenticated;
