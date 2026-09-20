import { supabase } from './supabase'
import type { Entry, Friendship, GuestbookEntry, Profile, Section, SectionKind, Visibility } from './types'

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
  const today = new Date().toISOString().slice(0, 10)
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
