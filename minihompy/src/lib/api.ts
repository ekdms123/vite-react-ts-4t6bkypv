import { supabase } from './supabase'
import { dayKey, todayKey } from './day'
import type { Comment, Entry, Friendship, GuestbookEntry, Profile, Section, SectionKind } from './types'

/* ── 프로필 ─────────────────────────────────────────── */

export async function getProfileByHandle(handle: string) {
  const { data, error } = await supabase
    .from('profiles').select('*').eq('handle', handle).maybeSingle()
  if (error) throw error
  return data as Profile | null
}

export async function getProfileById(id: string) {
  const { data, error } = await supabase
    .from('profiles').select('*').eq('id', id).maybeSingle()
  if (error) throw error
  return data as Profile | null
}

export async function updateProfile(id: string, patch: Partial<Profile>) {
  const { data, error } = await supabase
    .from('profiles').update(patch).eq('id', id).select().single()
  if (error) throw error
  return data as Profile
}

/** 주소는 사람이 읽는 값이라 모양을 강제한다. 중복은 DB의 unique가 잡는다. */
export function normalizeHandle(raw: string) {
  return raw.trim().toLowerCase().replace(/[^a-z0-9_]/g, '').slice(0, 20)
}

export async function isHandleFree(handle: string, selfId: string) {
  const { data, error } = await supabase
    .from('profiles').select('id').eq('handle', handle).maybeSingle()
  if (error) throw error
  return !data || data.id === selfId
}

/* ── 탭 ─────────────────────────────────────────────── */

export async function listSections(owner: string) {
  const { data, error } = await supabase
    .from('sections').select('*').eq('owner', owner).order('position')
  if (error) throw error
  return (data ?? []) as Section[]
}

export async function createSection(
  owner: string, label: string, kind: SectionKind, position: number,
) {
  const { data, error } = await supabase
    .from('sections').insert({ owner, label, kind, position }).select().single()
  if (error) throw error
  return data as Section
}

export async function updateSection(id: string, patch: Partial<Section>) {
  const { error } = await supabase.from('sections').update(patch).eq('id', id)
  if (error) throw error
}

export async function deleteSection(id: string) {
  const { error } = await supabase.from('sections').delete().eq('id', id)
  if (error) throw error
}

/* ── 글·사진·일정 ───────────────────────────────────── */

export async function listEntries(sectionId: string) {
  const { data, error } = await supabase
    .from('entries').select('*').eq('section_id', sectionId)
    .order('created_at', { ascending: false })
  if (error) throw error
  return (data ?? []) as Entry[]
}

export async function createEntry(row: Partial<Entry> & {
  section_id: string; owner: string
}) {
  const { data, error } = await supabase.from('entries').insert(row).select().single()
  if (error) throw error
  return data as Entry
}

export async function updateEntry(id: string, patch: Partial<Entry>) {
  const { error } = await supabase
    .from('entries').update({ ...patch, updated_at: new Date().toISOString() }).eq('id', id)
  if (error) throw error
}

export async function deleteEntry(id: string) {
  const { error } = await supabase.from('entries').delete().eq('id', id)
  if (error) throw error
}

/** 홈 화면의 'Updated news' — 여러 탭을 가로질러 최근 것만. */
export async function recentEntries(owner: string, limit = 5) {
  const { data, error } = await supabase
    .from('entries').select('*, sections(label, kind)')
    .eq('owner', owner).order('created_at', { ascending: false }).limit(limit)
  if (error) throw error
  return (data ?? []) as (Entry & { sections: { label: string; kind: SectionKind } })[]
}

export async function countsBySection(owner: string) {
  const { data, error } = await supabase
    .from('entries').select('section_id').eq('owner', owner)
  if (error) throw error
  const out: Record<string, number> = {}
  for (const row of data ?? []) out[row.section_id] = (out[row.section_id] ?? 0) + 1
  return out
}

/* ── 방명록 ─────────────────────────────────────────── */

export async function listGuestbook(home: string) {
  const { data, error } = await supabase
    .from('guestbook')
    .select('*, author_profile:profiles!guestbook_author_fkey(handle, title, avatar_url)')
    .eq('home', home).order('created_at', { ascending: false })
  if (error) throw error
  return (data ?? []) as GuestbookEntry[]
}

export async function signGuestbook(
  home: string, author: string, body: string, isSecret: boolean,
) {
  const { error } = await supabase
    .from('guestbook').insert({ home, author, body, is_secret: isSecret })
  if (error) throw error
}

export async function deleteGuestbookEntry(id: string) {
  const { error } = await supabase.from('guestbook').delete().eq('id', id)
  if (error) throw error
}

/* ── 일촌 ───────────────────────────────────────────── */

export async function listFriendships(me: string) {
  const { data, error } = await supabase
    .from('friendships').select('*')
    .or(`requester.eq.${me},addressee.eq.${me}`)
  if (error) throw error
  return (data ?? []) as Friendship[]
}

export async function requestFriend(requester: string, addressee: string, note: string) {
  const { error } = await supabase
    .from('friendships').insert({ requester, addressee, requester_note: note })
  if (error) throw error
}

export async function acceptFriend(id: string, note: string) {
  const { error } = await supabase.from('friendships')
    .update({ status: 'accepted', addressee_note: note, accepted_at: new Date().toISOString() })
    .eq('id', id)
  if (error) throw error
}

export async function removeFriend(id: string) {
  const { error } = await supabase.from('friendships').delete().eq('id', id)
  if (error) throw error
}

/** 일촌 목록에 이름을 붙이려면 프로필을 따로 읽어야 한다. */
export async function profilesByIds(ids: string[]) {
  if (!ids.length) return []
  const { data, error } = await supabase.from('profiles').select('*').in('id', ids)
  if (error) throw error
  return (data ?? []) as Profile[]
}

/* ── 사진 업로드 ────────────────────────────────────── */

/**
 * Storage 경로 첫 칸을 uid로 둔다. 스토리지 정책이 이 칸을 보고
 * '본인 폴더에만 쓰기'를 강제하므로, 경로 모양이 곧 권한이다.
 */
export async function uploadImage(uid: string, file: File, folder = 'photos') {
  const ext = file.name.split('.').pop()?.toLowerCase() ?? 'jpg'
  const path = `${uid}/${folder}/${Date.now()}-${Math.random().toString(36).slice(2, 8)}.${ext}`
  const { error } = await supabase.storage.from('media')
    .upload(path, file, { cacheControl: '3600', upsert: false })
  if (error) throw error
  return supabase.storage.from('media').getPublicUrl(path).data.publicUrl
}

/* ── 방문 카운터 ────────────────────────────────────── */

export async function bumpVisit(home: string) {
  const { error } = await supabase.rpc('bump_visit', { home_id: home })
  if (error) throw error
}

export async function getVisitCounts(home: string) {
  const today = todayKey()
  const [{ data: t }, { data: p }] = await Promise.all([
    supabase.from('visits').select('count').eq('home', home).eq('day', today).maybeSingle(),
    supabase.from('profiles').select('total_visits').eq('id', home).maybeSingle(),
  ])
  return { today: t?.count ?? 0, total: p?.total_visits ?? 0 }
}

/* ── 백업 ───────────────────────────────────────────── */

/** DB가 1차, 이 JSON이 2차. 무료 티어가 멈춰도 내용은 손에 남는다. */
export async function exportBackup(owner: string) {
  const [profile, sections, guestbook, friendships] = await Promise.all([
    getProfileById(owner),
    listSections(owner),
    listGuestbook(owner),
    listFriendships(owner),
  ])
  const { data: entries, error } = await supabase
    .from('entries').select('*').eq('owner', owner)
  if (error) throw error
  return {
    exported_at: new Date().toISOString(),
    schema: 'minihompy/1',
    profile, sections, entries: entries ?? [], guestbook, friendships,
  }
}

export function downloadJson(name: string, payload: unknown) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = name
  a.click()
  URL.revokeObjectURL(a.href)
}

/* ── 오늘 화면이 묻는 것들 ──────────────────────────── */

/** 마감이 지났거나 오늘까지인, 아직 안 끝난 일. 탭을 가로질러 모은다. */
export async function dueSoon(owner: string, days = 3) {
  const until = new Date(); until.setDate(until.getDate() + days)
  const { data, error } = await supabase
    .from('entries').select('*, sections(label)')
    .eq('owner', owner).eq('done', false)
    .not('due_at', 'is', null).lte('due_at', until.toISOString())
    .order('due_at')
  if (error) throw error
  return (data ?? []) as (Entry & { sections: { label: string } })[]
}

/** 아직 안 끝난 할 일. 오늘 화면은 여기서 에너지만큼만 잘라 쓴다. */
export async function openTodos(owner: string) {
  const { data, error } = await supabase
    .from('entries').select('*, sections(label, kind)')
    .eq('owner', owner).eq('done', false)
    .order('due_at', { ascending: true, nullsFirst: false })
    .order('created_at', { ascending: true })
  if (error) throw error
  return (data ?? []).filter(
    (r: any) => r.sections?.kind === 'todo',
  ) as (Entry & { sections: { label: string; kind: SectionKind } })[]
}

export async function toggleDone(id: string, done: boolean) {
  const { error } = await supabase.from('entries')
    .update({ done, done_at: done ? new Date().toISOString() : null })
    .eq('id', id)
  if (error) throw error
}

/* ── 가계부 ─────────────────────────────────────────── */

/** 쓸 생각이던 돈과 실제로 쓴 돈을 갈라서 돌려준다. 합계가 아니라 그 차이가 질문이다. */
export async function monthMoney(sectionId: string, month: Date) {
  const from = new Date(month.getFullYear(), month.getMonth(), 1)
  const to   = new Date(month.getFullYear(), month.getMonth() + 1, 1)
  const { data, error } = await supabase
    .from('entries').select('*').eq('section_id', sectionId)
    .gte('created_at', from.toISOString()).lt('created_at', to.toISOString())
  if (error) throw error
  const rows = (data ?? []) as Entry[]
  const spent   = rows.filter(r => !r.is_planned).reduce((s, r) => s + (r.amount ?? 0), 0)
  const planned = rows.filter(r =>  r.is_planned).reduce((s, r) => s + (r.amount ?? 0), 0)
  const byCategory: Record<string, number> = {}
  for (const r of rows) {
    if (r.is_planned) continue
    const k = r.category || '기타'
    byCategory[k] = (byCategory[k] ?? 0) + (r.amount ?? 0)
  }
  return { rows, spent, planned, byCategory }
}

/* ── 챌린지 ─────────────────────────────────────────── */

/**
 * 연속과 누적을 따로 센다. 하루 빠졌다고 누적까지 0으로 돌리면
 * 한 번 끊긴 사람은 다시 안 온다. 끊기는 건 연속뿐이다.
 */
export function streakOf(dates: string[]) {
  const days = new Set(dates.map(dayKey))
  const cur = new Date()
  if (!days.has(dayKey(cur))) cur.setDate(cur.getDate() - 1)
  let streak = 0
  while (days.has(dayKey(cur))) { streak++; cur.setDate(cur.getDate() - 1) }
  return { streak, total: days.size }
}

export async function challengeLog(sectionId: string) {
  const { data, error } = await supabase
    .from('entries').select('*').eq('section_id', sectionId)
    .order('created_at', { ascending: false })
  if (error) throw error
  return (data ?? []) as Entry[]
}

/* ── 캡처 ───────────────────────────────────────────── */

/**
 * 무엇이든 일단 받는 입구. 어디에 넣을지 고르는 그 결정이 제일 비싸서,
 * 분류를 나중으로 미룰 수 있어야 애초에 적는다. 보관함으로 떨어진다.
 */
export async function captureTo(owner: string, sections: Section[], text: string) {
  const inbox = sections.find(s => s.kind === 'free') ?? sections[0]
  if (!inbox) throw new Error('받을 곳이 없다')
  const firstLine = text.trim().split('\n')[0].slice(0, 60)
  return createEntry({
    section_id: inbox.id, owner,
    title: firstLine, body: text.trim(), visibility: inbox.visibility,
  })
}

/** 캡처한 걸 나중에 제자리로 옮긴다. 분류는 여유 있을 때 한다. */
export async function moveEntry(id: string, sectionId: string) {
  const { error } = await supabase.from('entries')
    .update({ section_id: sectionId }).eq('id', id)
  if (error) throw error
}

/* ── 사진 댓글 ──────────────────────────────────────── */

export async function listComments(entryId: string) {
  const { data, error } = await supabase
    .from('comments')
    .select('*, author_profile:profiles!comments_author_fkey(handle, title, avatar_url)')
    .eq('entry_id', entryId).order('created_at')
  if (error) throw error
  return (data ?? []) as Comment[]
}

export async function addComment(entryId: string, author: string, body: string) {
  const { error } = await supabase
    .from('comments').insert({ entry_id: entryId, author, body })
  if (error) throw error
}

export async function deleteComment(id: string) {
  const { error } = await supabase.from('comments').delete().eq('id', id)
  if (error) throw error
}

/** 목록 화면에서 사진마다 댓글 수를 보여주려면 한 번에 세어야 한다. */
export async function commentCounts(entryIds: string[]) {
  if (!entryIds.length) return {}
  const { data, error } = await supabase
    .from('comments').select('entry_id').in('entry_id', entryIds)
  if (error) throw error
  const out: Record<string, number> = {}
  for (const r of data ?? []) out[r.entry_id] = (out[r.entry_id] ?? 0) + 1
  return out
}

/* ── 앨범 ───────────────────────────────────────────── */

/** 앨범은 category 칸을 쓴다. 비어 있으면 '기본'으로 모은다. */
export async function listAlbums(sectionId: string) {
  const { data, error } = await supabase
    .from('entries').select('category, images, created_at')
    .eq('section_id', sectionId).order('created_at', { ascending: false })
  if (error) throw error
  const m = new Map<string, { name: string; count: number; cover: string | null }>()
  for (const r of (data ?? []) as Pick<Entry, 'category' | 'images' | 'created_at'>[]) {
    const name = r.category || '기본'
    const cur = m.get(name) ?? { name, count: 0, cover: null }
    cur.count += r.images.length || 1
    if (!cur.cover && r.images[0]) cur.cover = r.images[0]
    m.set(name, cur)
  }
  return [...m.values()]
}

export async function listInAlbum(sectionId: string, album: string) {
  let q = supabase.from('entries').select('*').eq('section_id', sectionId)
  q = album === '기본' ? q.or('category.is.null,category.eq.기본') : q.eq('category', album)
  const { data, error } = await q.order('created_at', { ascending: false })
  if (error) throw error
  return (data ?? []) as Entry[]
}

export async function renameAlbum(sectionId: string, from: string, to: string) {
  const { error } = await supabase.from('entries')
    .update({ category: to }).eq('section_id', sectionId).eq('category', from)
  if (error) throw error
}

/* ── 가계부 통계 ────────────────────────────────────── */

/** 이번 달과 지난달을 같이 돌려준다. 혼자 있는 숫자는 크고 작음을 말해주지 못한다. */
export async function moneyStats(sectionId: string, month: Date) {
  const start = new Date(month.getFullYear(), month.getMonth() - 1, 1)
  const end   = new Date(month.getFullYear(), month.getMonth() + 1, 1)
  const { data, error } = await supabase
    .from('entries').select('*').eq('section_id', sectionId)
    .gte('created_at', start.toISOString()).lt('created_at', end.toISOString())
  if (error) throw error
  const rows = (data ?? []) as Entry[]
  const inMonth = (r: Entry, offset: number) => {
    const d = new Date(r.created_at)
    return d.getFullYear() === month.getFullYear() &&
           d.getMonth() === month.getMonth() + offset
  }
  const sum = (rs: Entry[]) => rs.reduce((s, r) => s + (r.amount ?? 0), 0)

  const now  = rows.filter(r => inMonth(r, 0))
  const prev = rows.filter(r => inMonth(r, -1))
  const spend = (rs: Entry[]) => rs.filter(r => !r.is_planned && !r.is_income)

  const byCategory: Record<string, number> = {}
  for (const r of spend(now)) {
    const k = r.category || '기타'
    byCategory[k] = (byCategory[k] ?? 0) + (r.amount ?? 0)
  }
  // 일별 추이 — 어느 날 몰아 썼는지가 카테고리 합계보다 자주 답이 된다.
  const days = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate()
  const daily = Array.from({ length: days }, () => 0)
  for (const r of spend(now)) daily[new Date(r.created_at).getDate() - 1] += r.amount ?? 0

  return {
    rows: now,
    spent:   sum(spend(now)),
    prev:    sum(spend(prev)),
    income:  sum(now.filter(r => r.is_income)),
    planned: sum(now.filter(r => r.is_planned && !r.is_income)),
    byCategory, daily,
    biggest: spend(now).sort((a, b) => (b.amount ?? 0) - (a.amount ?? 0))[0] ?? null,
  }
}

/* ── 일정 옮기기 ────────────────────────────────────── */

export async function moveEvent(id: string, when: Date) {
  const { error } = await supabase.from('entries')
    .update({ starts_at: when.toISOString() }).eq('id', id)
  if (error) throw error
}

/* ── 검색 ───────────────────────────────────────────── */

/**
 * 탭을 가로질러 찾는다. 세 달쯤 지나면 "그때 그거"가 어느 탭에 있었는지
 * 기억나지 않는데, 그때 탭을 하나씩 뒤지게 만들면 그냥 포기한다.
 */
export async function searchAll(owner: string, q: string, limit = 40) {
  const term = q.trim()
  if (term.length < 1) return []
  const like = `%${term}%`
  const { data, error } = await supabase
    .from('entries').select('*, sections(label, kind)')
    .eq('owner', owner)
    .or(`title.ilike.${like},body.ilike.${like},category.ilike.${like}`)
    .order('created_at', { ascending: false })
    .limit(limit)
  if (error) throw error
  return (data ?? []) as (Entry & { sections: { label: string; kind: SectionKind } })[]
}

/* ── 일촌평 ─────────────────────────────────────────── */

/** 대문의 "What friends say". 나를 어떻게 적어뒀는지 모아 온다. */
export async function wordsFromFriends(home: string, limit = 4) {
  const { data, error } = await supabase
    .from('friendships').select('*').eq('status', 'accepted')
    .or(`requester.eq.${home},addressee.eq.${home}`)
  if (error) throw error
  const rows = (data ?? []) as Friendship[]
  const out: { who: string; note: string }[] = []
  const ids: string[] = []
  for (const f of rows) {
    // 상대가 나를 두고 적은 쪽만 고른다
    const note = f.requester === home ? f.addressee_note : f.requester_note
    const other = f.requester === home ? f.addressee : f.requester
    if (note?.trim()) { out.push({ who: other, note: note.trim() }); ids.push(other) }
  }
  if (!out.length) return []
  const people = await profilesByIds(ids)
  const byId = Object.fromEntries(people.map(p => [p.id, p.title]))
  return out.slice(0, limit).map(o => ({ who: byId[o.who] ?? '누군가', note: o.note }))
}
