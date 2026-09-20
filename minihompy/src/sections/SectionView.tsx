import { useEffect, useRef, useState } from 'react'
import * as api from '../lib/api'
import { EMPTY_NOTE, MOODS, type Entry, type Profile, type Section } from '../lib/types'
import Todo from './Todo'
import Ledger from './Ledger'
import Challenge from './Challenge'
import Calendar from './Calendar'

interface Props {
  section: Section
  owner: Profile
  isOwner: boolean
  uid: string | null
}

/** 탭 하나를 그린다. 어떻게 그릴지는 section.kind 가 고른다. */
export default function SectionView({ section, owner, isOwner, uid }: Props) {
  const [entries, setEntries] = useState<Entry[]>([])
  const [loading, setLoading] = useState(true)
  const [composing, setComposing] = useState(false)

  async function reload() {
    setLoading(true)
    try { setEntries(await api.listEntries(section.id)) }
    finally { setLoading(false) }
  }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [section.id])

  // kind 가 렌더러를 고른다. 탭을 늘리는 건 코드가 아니라 데이터다.
  if (section.kind === 'guestbook') return <Guestbook owner={owner} uid={uid} isOwner={isOwner} />
  if (section.kind === 'todo')      return <Todo      section={section} isOwner={isOwner} uid={uid} />
  if (section.kind === 'ledger')    return <Ledger    section={section} isOwner={isOwner} uid={uid} />
  if (section.kind === 'challenge') return <Challenge section={section} isOwner={isOwner} uid={uid} />
  if (section.kind === 'calendar')  return <Calendar  section={section} isOwner={isOwner} uid={uid} />

  return (
    <div>
      <div className="sec-title" style={{ display: 'flex', alignItems: 'center' }}>
        <span>{section.label}</span>
        <span style={{ marginLeft: 'auto', color: '#b0b0b0', fontWeight: 400 }}>
          {entries.length}
        </span>
        {isOwner && (
          <button className="btn ghost" style={{ marginLeft: 8 }}
                  onClick={() => setComposing(v => !v)}>
            {composing ? '닫기' : '+ 쓰기'}
          </button>
        )}
      </div>

      {composing && (
        <Composer section={section} uid={uid!} onDone={() => { setComposing(false); void reload() }} />
      )}

      {loading ? <div className="empty-note">불러오는 중…</div>
        : entries.length === 0
          ? <div className="empty-note">
              {EMPTY_NOTE[section.kind].split('\n').map((line, i) => (
                <span key={i}>{line}<br /></span>
              ))}
            </div>
          : <EntryList section={section} entries={entries} isOwner={isOwner} onChange={reload} />}
    </div>
  )
}

/* ── 목록 ───────────────────────────────────────────── */

function EntryList({ section, entries, isOwner, onChange }: {
  section: Section; entries: Entry[]; isOwner: boolean; onChange: () => void
}) {
  async function remove(id: string) {
    if (!confirm('지울까?')) return
    await api.deleteEntry(id); onChange()
  }

  if (section.kind === 'photo') {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(104px,1fr))', gap: 8 }}>
        {entries.flatMap(e => e.images.map((src, i) => (
          <figure key={`${e.id}-${i}`} style={{ margin: 0 }}>
            <img src={src} alt={e.title || '사진'} loading="lazy"
                 style={{ width: '100%', aspectRatio: '1/1', objectFit: 'cover',
                          border: '1px solid var(--line)', borderRadius: 6 }} />
            {e.title && <figcaption style={{ fontSize: 10, color: 'var(--ink-soft)',
                                             paddingTop: 3, textAlign: 'center' }}>{e.title}</figcaption>}
          </figure>
        )))}
      </div>
    )
  }

  if (section.kind === 'jukebox') {
    return (
      <div style={{ display: 'grid', gap: 12 }}>
        {entries.map(e => {
          const id = youtubeId(String(e.meta?.url ?? e.body))
          return (
            <div key={e.id}>
              <div style={{ fontWeight: 700, paddingBottom: 4 }}>{e.title || '무제'}</div>
              {id
                ? <iframe width="100%" height="180" src={`https://www.youtube.com/embed/${id}`}
                          title={e.title} allowFullScreen style={{ border: 0, borderRadius: 6 }} />
                : <a href={String(e.meta?.url ?? '')} target="_blank" rel="noreferrer">링크 열기</a>}
              {isOwner && <button className="btn ghost" onClick={() => remove(e.id)}>지우기</button>}
            </div>
          )
        })}
      </div>
    )
  }

  // diary · board · free 는 같은 글 모양을 쓰되 머리말만 다르다.
  return (
    <div style={{ display: 'grid', gap: 14 }}>
      {entries.map(e => (
        <article key={e.id} style={{ borderBottom: '1px solid var(--line)', paddingBottom: 12 }}>
          <header style={{ display: 'flex', alignItems: 'baseline', gap: 8, paddingBottom: 4 }}>
            <h3 style={{ margin: 0, fontSize: 12, color: 'var(--title)' }}>
              {e.title || '(제목 없음)'}
            </h3>
            {section.kind === 'diary' && e.mood && <span className="chip">{e.mood}</span>}
            <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--ink-soft)' }}>
              {new Date(e.created_at).toLocaleDateString('ko-KR')}
            </span>
            {isOwner && <button className="btn ghost" onClick={() => remove(e.id)}>×</button>}
          </header>
          {e.body && <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.75 }}>{e.body}</div>}
          {e.images.length > 0 && (
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', paddingTop: 8 }}>
              {e.images.map((src, i) => (
                <img key={i} src={src} alt="" loading="lazy"
                     style={{ maxWidth: 180, borderRadius: 6, border: '1px solid var(--line)' }} />
              ))}
            </div>
          )}
        </article>
      ))}
    </div>
  )
}

/* ── 작성 ───────────────────────────────────────────── */

function Composer({ section, uid, onDone }: {
  section: Section; uid: string; onDone: () => void
}) {
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [mood, setMood] = useState('')
  const [startsAt, setStartsAt] = useState('')
  const [url, setUrl] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  async function submit() {
    setBusy(true); setErr('')
    try {
      const images: string[] = []
      for (const f of files) images.push(await api.uploadImage(uid, f, section.kind))
      await api.createEntry({
        section_id: section.id, owner: uid,
        title, body, images,
        mood: section.kind === 'diary' ? mood : null,
        starts_at: section.kind === 'calendar' && startsAt
          ? new Date(startsAt).toISOString() : null,
        meta: section.kind === 'jukebox' ? { url } : {},
        visibility: section.visibility,
      })
      onDone()
    } catch (e) {
      setErr(e instanceof Error ? e.message : '저장 실패')
    } finally { setBusy(false) }
  }

  return (
    <div style={{ border: '1px solid var(--line)', borderRadius: 8, padding: 10,
                  marginBottom: 12, display: 'grid', gap: 7, background: '#fcfdfe' }}>
      <input type="text" placeholder="제목" value={title}
             onChange={e => setTitle(e.target.value)} />

      {section.kind === 'diary' && (
        <select value={mood} onChange={e => setMood(e.target.value)}>
          {MOODS.map(m => <option key={m} value={m}>{m || '기분 —'}</option>)}
        </select>
      )}
      {section.kind === 'calendar' && (
        <input type="datetime-local" value={startsAt}
               onChange={e => setStartsAt(e.target.value)} />
      )}
      {section.kind === 'jukebox' && (
        <input type="text" placeholder="유튜브 주소" value={url}
               onChange={e => setUrl(e.target.value)} />
      )}

      {section.kind !== 'jukebox' && (
        <textarea rows={section.kind === 'photo' ? 2 : 5} placeholder="내용"
                  value={body} onChange={e => setBody(e.target.value)} />
      )}

      {(section.kind === 'photo' || section.kind === 'diary' || section.kind === 'free') && (
        <input type="file" accept="image/*" multiple
               onChange={e => setFiles(Array.from(e.target.files ?? []))} />
      )}

      {err && <div style={{ color: '#c0392b', fontSize: 11 }}>{err}</div>}
      <div style={{ display: 'flex', gap: 6 }}>
        <button className="btn" onClick={submit} disabled={busy}>
          {busy ? '올리는 중…' : '올리기'}
        </button>
      </div>
    </div>
  )
}

/* ── 방명록 ─────────────────────────────────────────── */

function Guestbook({ owner, uid, isOwner }: {
  owner: Profile; uid: string | null; isOwner: boolean
}) {
  const [rows, setRows] = useState<Awaited<ReturnType<typeof api.listGuestbook>>>([])
  const [body, setBody] = useState('')
  const [secret, setSecret] = useState(false)
  const [busy, setBusy] = useState(false)
  const boxRef = useRef<HTMLTextAreaElement>(null)

  async function reload() { setRows(await api.listGuestbook(owner.id)) }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [owner.id])

  async function submit() {
    if (!uid || !body.trim()) return
    setBusy(true)
    try {
      await api.signGuestbook(owner.id, uid, body.trim(), secret)
      setBody(''); setSecret(false); await reload()
      boxRef.current?.focus()
    } finally { setBusy(false) }
  }

  return (
    <div>
      <div className="sec-title">방명록 <span style={{ color: '#b0b0b0', fontWeight: 400 }}>{rows.length}</span></div>

      {uid ? (
        <div style={{ display: 'grid', gap: 6, marginBottom: 14 }}>
          <textarea ref={boxRef} rows={3} placeholder="한마디 남기고 가기"
                    value={body} onChange={e => setBody(e.target.value)} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <label style={{ fontSize: 11, color: 'var(--ink-soft)', display: 'flex', gap: 4 }}>
              <input type="checkbox" checked={secret} style={{ width: 'auto' }}
                     onChange={e => setSecret(e.target.checked)} />
              비밀글
            </label>
            <button className="btn" style={{ marginLeft: 'auto' }}
                    onClick={submit} disabled={busy || !body.trim()}>남기기</button>
          </div>
        </div>
      ) : (
        <div className="empty-note">로그인하면 방명록을 남길 수 있다.</div>
      )}

      {rows.length === 0
        ? <div className="empty-note">아직 아무도 다녀가지 않았다.</div>
        : rows.map(g => (
          <div key={g.id} style={{ display: 'flex', gap: 8, padding: '9px 0',
                                   borderBottom: '1px solid var(--line)' }}>
            <div style={{ flex: '0 0 32px', height: 32, borderRadius: 4, overflow: 'hidden',
                          background: '#f2f2f2', border: '1px solid var(--line)' }}>
              {g.author_profile?.avatar_url &&
                <img src={g.author_profile.avatar_url} alt=""
                     style={{ width: '100%', height: '100%', objectFit: 'cover' }} />}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 11 }}>
                <b style={{ color: 'var(--title)' }}>{g.author_profile?.title ?? '누군가'}</b>
                <span style={{ color: 'var(--ink-soft)', marginLeft: 6 }}>
                  {new Date(g.created_at).toLocaleDateString('ko-KR')}
                </span>
                {g.is_secret && <span className="chip" style={{ marginLeft: 6 }}>비밀</span>}
              </div>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{g.body}</div>
            </div>
            {(isOwner || uid === g.author) && (
              <button className="btn ghost"
                      onClick={async () => { await api.deleteGuestbookEntry(g.id); await reload() }}>×</button>
            )}
          </div>
        ))}
    </div>
  )
}

function youtubeId(raw: string): string | null {
  const m = raw.match(/(?:youtu\.be\/|v=|embed\/)([A-Za-z0-9_-]{11})/)
  return m ? m[1] : null
}
