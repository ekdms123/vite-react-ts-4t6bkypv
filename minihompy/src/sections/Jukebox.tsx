import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import type { Entry, Section } from '../lib/types'

function youtubeId(raw: string): string | null {
  const m = String(raw).match(/(?:youtu\.be\/|v=|embed\/|shorts\/)([A-Za-z0-9_-]{11})/)
  return m ? m[1] : null
}

/** 한 곡만 크게 걸고 나머지는 목록으로. 미니홈피 BGM 자리다. */
export default function Jukebox({ section, isOwner, uid }: {
  section: Section; isOwner: boolean; uid: string | null
}) {
  const [rows, setRows] = useState<Entry[]>([])
  const [playing, setPlaying] = useState<Entry | null>(null)
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')

  async function reload() {
    const r = await api.listEntries(section.id)
    setRows(r); setPlaying(p => p ?? r[0] ?? null)
  }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [section.id])

  async function add() {
    if (!uid || !url.trim()) return
    if (!youtubeId(url)) { setMsg('유튜브 주소가 아닌 것 같다.'); return }
    setBusy(true); setMsg('')
    try {
      await api.createEntry({
        section_id: section.id, owner: uid,
        title: title.trim() || '무제', meta: { url: url.trim() },
        visibility: section.visibility,
      })
      setUrl(''); setTitle(''); await reload()
    } finally { setBusy(false) }
  }

  const nowId = playing ? youtubeId(String(playing.meta?.url ?? '')) : null

  return (
    <div>
      <div className="sec-title">
        {section.label}
        <span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>{rows.length}곡</span>
      </div>

      {playing && nowId && (
        <div className="deck">
          <div className="deck-screen">
            <iframe src={`https://www.youtube.com/embed/${nowId}`} title={playing.title}
                    allow="accelerometer; autoplay; encrypted-media; picture-in-picture"
                    allowFullScreen />
          </div>
          <div className="deck-label">
            <span className="reel" /> <b>{playing.title}</b> <span className="reel" />
          </div>
        </div>
      )}

      {isOwner && (
        <div className="quick-add">
          <input type="text" placeholder="유튜브 주소 붙여넣기" value={url}
                 onChange={e => setUrl(e.target.value)} />
          <input type="text" placeholder="곡 이름" value={title} style={{ maxWidth: 120 }}
                 onChange={e => setTitle(e.target.value)}
                 onKeyDown={e => { if (e.key === 'Enter') void add() }} />
          <button className="btn" onClick={add} disabled={busy || !url.trim()}>담기</button>
        </div>
      )}
      {msg && <div className="k soft" style={{ color: '#b0552f' }}>{msg}</div>}

      {rows.length === 0
        ? <div className="empty-note">아직 담은 곡이 없다.</div>
        : <ol className="tracklist">
            {rows.map((r, i) => (
              <li key={r.id} data-on={playing?.id === r.id}>
                <span className="no">{String(i + 1).padStart(2, '0')}</span>
                <button className="what" onClick={() => setPlaying(r)}>{r.title}</button>
                {playing?.id === r.id && <span className="eq"><i /><i /><i /></span>}
                {isOwner && (
                  <button className="x" onClick={async () => {
                    await api.deleteEntry(r.id)
                    if (playing?.id === r.id) setPlaying(null)
                    await reload()
                  }}>×</button>
                )}
              </li>
            ))}
          </ol>}
    </div>
  )
}
