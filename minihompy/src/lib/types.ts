/** 탭의 종류. 이 값이 어떤 렌더러와 에디터를 쓸지 고른다. */
export type SectionKind =
  | 'diary' | 'photo' | 'board' | 'calendar' | 'todo' | 'ledger' | 'challenge'
  | 'jukebox' | 'guestbook' | 'free'

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
  done: boolean
  done_at: string | null
  due_at: string | null
  amount: number | null
  category: string | null
  is_planned: boolean
  is_income: boolean
  decor: Record<string, unknown>
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
  todo:      '할 일',
  calendar:  '달력',
  diary:     '다이어리',
  photo:     '사진첩',
  ledger:    '가계부',
  challenge: '챌린지',
  board:     '게시판',
  jukebox:   '쥬크박스',
  free:      '보관함',
  guestbook: '방명록',
}

/** 빈 화면은 꾸짖지 않는다. 빈 날이 정상이라고 화면이 먼저 말해야
    놓친 뒤에 다시 돌아온다. */
export const EMPTY_NOTE: Record<SectionKind, string> = {
  todo:      '오늘은 비어 있다.\n하나만 적어도 충분하다.',
  calendar:  '이번 달은 아직 조용하다.',
  diary:     '아직 쓴 날이 없다.\n한 줄이면 된다.',
  photo:     '사진이 없다.',
  ledger:    '이번 달 기록이 없다.',
  challenge: '아직 챌린지가 없다.\n작은 걸로 하나만.',
  board:     '아직 글이 없다.',
  jukebox:   '아직 담은 곡이 없다.',
  free:      '여기엔 아무거나 던져도 된다.',
  guestbook: '아직 아무도 다녀가지 않았다.',
}

/** 탭을 새로 만들 때 고를 수 있는 종류 — 방명록은 하나면 충분하다. */
export const CREATABLE_KINDS: SectionKind[] =
  ['todo', 'calendar', 'diary', 'photo', 'ledger', 'challenge', 'board', 'jukebox', 'free']

export const MOODS = [
  '', '행복', '뿌듯', '설렘', '그냥그럼', '피곤', '심란', '우울', '신남', '멍함',
]

/** 컨디션이 나쁜 날 화면이 그대로면 앱을 닫는다. 상태가 보여줄 양을 정한다. */
export const ENERGY = [
  { key: 'low',   label: '낮음',     topN: 1 },
  { key: 'mid',   label: '보통',     topN: 3 },
  { key: 'high',  label: '하이퍼',   topN: 6 },
] as const
export type EnergyKey = typeof ENERGY[number]['key']

export const LEDGER_CATEGORIES = [
  '식비', '카페', '교통', '쇼핑', '구독', '취미', '건강', '공부', '경조사', '기타',
]

export const INCOME_CATEGORIES = ['월급', '용돈', '환급', '부수입', '기타']

export interface Comment {
  id: string
  entry_id: string
  author: string
  body: string
  created_at: string
  author_profile?: { handle: string; title: string; avatar_url: string | null }
}

/** 사진 한 장을 한 페이지로 꾸밀 때 쓰는 값들. */
export interface Decor extends Record<string, unknown> {
  bg?: string        // 배경색
  note?: string      // 사진 아래 적는 글
  frame?: string     // 테두리 모양
}
export const FRAMES = [
  { key: 'polaroid', label: '폴라로이드' },
  { key: 'film',     label: '필름' },
  { key: 'plain',    label: '그냥' },
  { key: 'lace',     label: '레이스' },
]
export const DECOR_BG = [
  '#ffffff', '#fff6e5', '#ffeef2', '#eaf4f8', '#eef7ee', '#f3eefa', '#2b2b30',
]

export const SKINS = [
  { key: 'sky',   label: '하늘' },
  { key: 'pink',  label: '핑크' },
  { key: 'mint',  label: '민트' },
  { key: 'night', label: '밤' },
]
