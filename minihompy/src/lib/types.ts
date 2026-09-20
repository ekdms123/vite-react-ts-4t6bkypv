/** 탭의 종류. 이 값이 어떤 렌더러와 에디터를 쓸지 고른다. */
export type SectionKind =
  | 'diary' | 'photo' | 'board' | 'calendar' | 'jukebox' | 'guestbook' | 'free'

export type Visibility = 'public' | 'friends' | 'private'

export interface Profile {
  id: string
  handle: string
  title: string
  tagline: string
  mood: string
  avatar_url: string | null
  skin_key: string
  bgm_url: string | null
  total_visits: number
  created_at: string
}

export interface Section {
  id: string
  owner: string
  label: string
  kind: SectionKind
  position: number
  visibility: Visibility
  created_at: string
}

export interface Entry {
  id: string
  section_id: string
  owner: string
  title: string
  body: string
  images: string[]
  mood: string | null
  weather: string | null
  starts_at: string | null
  ends_at: string | null
  meta: Record<string, unknown>
  visibility: Visibility
  created_at: string
  updated_at: string
}

export interface GuestbookEntry {
  id: string
  home: string
  author: string
  body: string
  is_secret: boolean
  created_at: string
  author_profile?: Pick<Profile, 'handle' | 'title' | 'avatar_url'>
}

export interface Friendship {
  id: string
  requester: string
  addressee: string
  status: 'pending' | 'accepted'
  requester_note: string
  addressee_note: string
  created_at: string
  accepted_at: string | null
}

export const KIND_LABEL: Record<SectionKind, string> = {
  diary:     '다이어리',
  photo:     '사진첩',
  board:     '게시판',
  calendar:  '일정',
  jukebox:   '쥬크박스',
  guestbook: '방명록',
  free:      '자유',
}

/** 탭을 새로 만들 때 고를 수 있는 종류 — 방명록은 하나면 충분하다. */
export const CREATABLE_KINDS: SectionKind[] =
  ['diary', 'photo', 'board', 'calendar', 'jukebox', 'free']

export const MOODS = [
  '', '행복', '뿌듯', '설렘', '그냥그럼', '피곤', '심란', '우울', '신남', '멍함',
]

export const SKINS = [
  { key: 'sky',   label: '하늘' },
  { key: 'pink',  label: '핑크' },
  { key: 'mint',  label: '민트' },
  { key: 'night', label: '밤' },
]
