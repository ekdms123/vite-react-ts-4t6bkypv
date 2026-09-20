-- 잠그기 2/2 — 초대한 사람만 가입
-- 07 을 먼저 하고 이걸 한다. 여러 번 돌려도 안전하다.

-- ── 3. 초대한 사람만 가입할 수 있다 ───────────────────────
create table if not exists allowed_emails (
  email      text primary key,
  note       text default '',
  created_at timestamptz not null default now()
);
alter table allowed_emails enable row level security;
-- 명단 자체는 아무에게도 보이지 않는다. 대시보드에서만 만진다.

create or replace function handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare new_handle text; gate int;
begin
  -- 명단이 비어 있으면 아직 아무도 없다는 뜻이라 통과시킨다.
  -- 그래야 첫 사람이 자기 집에서 잠길 일이 없다.
  select count(*) into gate from allowed_emails;
  if gate > 0 and not exists (
    select 1 from allowed_emails where lower(email) = lower(new.email)
  ) then
    raise exception '초대받지 않은 이메일입니다';
  end if;

  new_handle := 'u' || substr(replace(new.id::text, '-', ''), 1, 8);
  insert into profiles (id, handle) values (new.id, new_handle);
  insert into sections (owner, label, kind, position, visibility) values
    (new.id, '오늘',     'todo',      1, 'private'),
    (new.id, '달력',     'calendar',  2, 'private'),
    (new.id, '다이어리', 'diary',     3, 'private'),
    (new.id, '사진첩',   'photo',     4, 'friends'),
    (new.id, '가계부',   'ledger',    5, 'private'),
    (new.id, '챌린지',   'challenge', 6, 'friends'),
    (new.id, '쥬크박스', 'jukebox',   7, 'public'),
    (new.id, '보관함',   'free',      8, 'private'),
    (new.id, '방명록',   'guestbook', 9, 'public');
  return new;
end;
$$;

-- ── 4. 로그인 안 한 손님의 권한을 거둔다 ──────────────────
revoke all on all tables    in schema public from anon;
revoke all on all functions in schema public from anon;
revoke all on all sequences in schema public from anon;
