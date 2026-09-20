import { useEffect, useMemo, useState } from 'react'
import * as api from '../lib/api'
import type { Entry, Section } from '../lib/types'

const key = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
const WEEK = ['일', '월', '화', '수', '목', '금', '토']

/** 달을 한 판에 보여주고, 누른 날만 아래로 펼친다. */
export default function Calendar({ section, isOwner, uid }: {
  section: Section; isOwner: boolean; uid: string | null
}) {
  const [cursor, setCursor] = useState(() => new Date())
  const [rows, setRows] = useState<Entry[]>([])
  const [picked, setPicked] = useState(() => key(new Date()))
  const [title, setTitle] = useState('')
  const [time, setTime] = useState('')
  const [busy, setBusy] = useState(false)

  async function reload() { setRows(await api.listEntries(section.id)) }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [section.id])

  const byDay = useMemo(() => {
    const m: Record<string, Entry[]> = {}
    for (const r of rows) {
      if (!r.starts_at) continue
      const k = key(new Date(r.starts_at))
      ;(m[k] ??= []).push(r)
    }
    return m
  }, [rows])

  const cells = useMemo(() => {
    const first = new Date(cursor.getFullYear(), cursor.getMonth(), 1)
    const start = new Date(first); start.setDate(1 - first.getDay())
    return Array.from({ length: 42 }, (_, i) => {
      const d = new Date(start); d.setDate(start.getDate() + i)
      return { d, k: key(d), inMonth: d.getMonth() === cursor.getMonth() }
    })
  }, [cursor])

  async function add() {
    if (!uid || !title.trim()) return
    setBusy(true)
    try {
      const at = new Date(`${picked}T${time || '09:00'}`)
      await api.createEntry({
        section_id: section.id, owner: uid,
        title: title.trim(), starts_at: at.toISOString(),
        visibility: section.visibility,
      })
      setTitle(''); setTime(''); await reload()
    } finally { setBusy(false) }
  }

  const todayKey = key(new Date())
  const dayRows = (byDay[picked] ?? [])
    .sort((a, b) => (a.starts_at ?? '').localeCompare(b.starts_at ?? ''))

  return (
    <div>
      <div className="sec-title cal-head">
        <button className="nav" onClick={() => setCursor(c => new Date(c.getFullYear(), c.getMonth() - 1, 1))}>‹</button>
        <span>{cursor.getFullYear()}년 {cursor.getMonth() + 1}월</span>
        <button className="nav" onClick={() => setCursor(c => new Date(c.getFullYear(), c.getMonth() + 1, 1))}>›</button>
      </div>

      <div className="cal-grid">
        {WEEK.map((w, i) => (
          <div key={w} className="cal-wd" data-sun={i === 0} data-sat={i === 6}>{w}</div>
        ))}
        {cells.map(c => (
          <button key={c.k} className="cal-day"
                  data-dim={!c.inMonth} data-today={c.k === todayKey} data-picked={c.k === picked}
                  onClick={() => setPicked(c.k)}>
            <span>{c.d.getDate()}</span>
            {byDay[c.k]?.length ? <i className="dot" data-n={Math.min(3, byDay[c.k].length)} /> : null}
          </button>
        ))}
      </div>

      <div className="cal-day-panel">
        <div className="k">{picked.replace(/-/g, '.')}</div>
        {dayRows.length === 0
          ? <div className="empty-note" style={{ padding: '14px 8px' }}>비어 있는 날.</div>
          : <ul className="day-list">
              {dayRows.map(r => (
                <li key={r.id}>
                  <time>{new Date(r.starts_at!).toLocaleTimeString('ko-KR',
                    { hour: '2-digit', minute: '2-digit' })}</time>
                  <span className="what">{r.title}</span>
                  {isOwner && (
                    <button className="x"
                            onClick={async () => { await api.deleteEntry(r.id); await reload() }}>×</button>
                  )}
                </li>
              ))}
            </ul>}

        {isOwner && (
          <div className="quick-add">
            <input type="time" value={time} onChange={e => setTime(e.target.value)} style={{ width: 96 }} />
            <input type="text" placeholder="무슨 일" value={title}
                   onChange={e => setTitle(e.target.value)}
                   onKeyDown={e => { if (e.key === 'Enter') void add() }} />
            <button className="btn" onClick={add} disabled={busy || !title.trim()}>담기</button>
          </div>
        )}
      </div>
    </div>
  )
}
