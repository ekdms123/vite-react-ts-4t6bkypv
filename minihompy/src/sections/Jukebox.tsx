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
  // 브라우저는 소리 있는 자동재생을 사람이 한 번 누르기 전에는 막는다.
  // 그래서 첫 곡은 가만히 두고, 사람이 곡을 고른 순간부터 이어서 튼다.
  const [auto, setAuto] = useState(false)

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
  const src = nowId
    ? `https://www.youtube.com/embed/${nowId}?autoplay=${auto ? 1 : 0}&rel=0&playsinline=1`
    : null

  function play(r: Entry) { setPlaying(r); setAuto(true) }

  return (
    <div>
      <div className="sec-title">
        {section.label}
        <span style={{ float: 'right', fontWeight: 400, color: '#636363' }}>{rows.length}곡</span>
      </div>

      {playing && src && (
        <div className="deck">
          <div className="deck-screen">
            <iframe key={playing.id} src={src!} title={playing.title}
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
                <button className="what" onClick={() => play(r)}>{r.title}</button>
                {playing?.id === r.id && <span className="eq"><i /><i /><i /></span>}
                {isOwner && (
                  <button className="x" aria-label="지우기" onClick={async () => {
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
