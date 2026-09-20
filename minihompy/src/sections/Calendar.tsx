import { useEffect, useMemo, useState } from 'react'
import * as api from '../lib/api'
import type { Entry, Section } from '../lib/types'
import Editable from '../components/Editable'
import { dayKey as key } from '../lib/day'


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
  // 옮길 일정을 하나 집어두면, 다음에 누른 날짜가 목적지가 된다.
  // 폰에서 끌어다 놓기는 잘 안 되므로 집고-놓기 두 번 누르기로 한다.
  const [moving, setMoving] = useState<Entry | null>(null)

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
                  data-drop={moving !== null}
                  onClick={async () => {
                    if (moving) {
                      const old = new Date(moving.starts_at!)
                      const to = new Date(`${c.k}T00:00`)
                      to.setHours(old.getHours(), old.getMinutes())
                      await api.moveEvent(moving.id, to)
                      setMoving(null); setPicked(c.k); await reload()
                      return
                    }
                    setPicked(c.k)
                  }}>
            <span>{c.d.getDate()}</span>
            {byDay[c.k]?.length ? <i className="dot" data-n={Math.min(3, byDay[c.k].length)} /> : null}
          </button>
        ))}
      </div>

      {moving && (
        <div className="move-hint">
          <b>{moving.title}</b> — 옮길 날짜를 누르세요
          <button className="crumb" onClick={() => setMoving(null)}>취소</button>
        </div>
      )}

      <div className="cal-day-panel">
        <div className="k">{picked.replace(/-/g, '.')}</div>
        {dayRows.length === 0
          ? <div className="empty-note" style={{ padding: '14px 8px' }}>비어 있는 날.</div>
          : <ul className="day-list">
              {dayRows.map(r => (
                <li key={r.id} data-moving={moving?.id === r.id}>
                  <time>{new Date(r.starts_at!).toLocaleTimeString('ko-KR',
                    { hour: '2-digit', minute: '2-digit' })}</time>
                  <Editable className="what" value={r.title} disabled={!isOwner}
                            onSave={async next => {
                              await api.updateEntry(r.id, { title: next }); await reload()
                            }} />
                  {isOwner && (
                    <>
                      <button className="crumb move"
                              onClick={() => setMoving(moving?.id === r.id ? null : r)}>
                        {moving?.id === r.id ? '취소' : '옮기기'}
                      </button>
                      <button className="x"
                              onClick={async () => { await api.deleteEntry(r.id); await reload() }}>×</button>
                    </>
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
