-- 기본 공개범위를 닫는 쪽으로
--
-- 1단계에서는 탭이 전부 'public'으로 깔렸다. 컬럼 기본값이 public인데
-- 가입 트리거가 visibility를 지정하지 않았기 때문이다. 미니홈피니까 공개가
-- 기본인 건 맞지만 그건 대문·방명록 얘기고, 가계부와 할 일까지 로그인한
-- 아무나 보게 두는 건 다른 문제다.
--
-- 잘못 닫히면 본인이 열면 되고, 잘못 열리면 이미 남이 본 뒤다.
-- 그래서 모르면 닫는다.
--
-- 이 파일 전체를 SQL Editor에 붙여넣고 Run. 여러 번 돌려도 안전하다.

-- 새로 가입하는 사람에게 적용
create or replace function handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare new_handle text;
begin
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

-- 이미 가입한 사람의 탭도 같은 기준으로 옮긴다.
-- 본인이 이미 손댄 탭은 건드리지 않도록 'public'인 것만 내린다.
update sections set visibility = 'private'
 where visibility = 'public' and kind in ('todo','calendar','diary','ledger','free');

update sections set visibility = 'friends'
 where visibility = 'public' and kind in ('photo','challenge');

-- 글도 같이 내린다. 탭을 닫아도 글이 public이면 의미가 없다.
update entries e set visibility = s.visibility
  from sections s
 where s.id = e.section_id and e.visibility = 'public' and s.visibility <> 'public';

-- 앞으로 새로 만드는 탭과 글의 기본값도 닫는다.
alter table sections alter column visibility set default 'private';
alter table entries  alter column visibility set default 'private';
