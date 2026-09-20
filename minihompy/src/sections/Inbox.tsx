import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import { KIND_LABEL, type Entry, type Section } from '../lib/types'

/**
 * 던져둔 것들이 쌓이는 곳. 여기의 일은 보관이 아니라 비우기다.
 * 그래서 메모마다 "어디로 보낼지"가 바로 붙어 있다.
 */
export default function Inbox({ section, sections, isOwner, uid }: {
  section: Section; sections: Section[]; isOwner: boolean; uid: string | null
}) {
  const [rows, setRows] = useState<Entry[]>([])
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)

  async function reload() { setRows(await api.listEntries(section.id)) }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [section.id])

  async function add() {
    if (!uid || !note.trim()) return
    setBusy(true)
    try {
      await api.createEntry({
        section_id: section.id, owner: uid,
        title: note.trim().split('\n')[0].slice(0, 50), body: note.trim(),
        visibility: section.visibility,
      })
      setNote(''); await reload()
    } finally { setBusy(false) }
  }

  const targets = sections.filter(s => s.id !== section.id && s.kind !== 'guestbook')

  return (
    <div>
      <div className="sec-title">
        {section.label}
        <span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>{rows.length}장</span>
      </div>

      {isOwner && (
        <div className="quick-add">
          <input type="text" placeholder="아무거나 던져두기" value={note}
                 onChange={e => setNote(e.target.value)}
                 onKeyDown={e => { if (e.key === 'Enter') void add() }} />
          <button className="btn" onClick={add} disabled={busy || !note.trim()}>붙이기</button>
        </div>
      )}

      {rows.length === 0
        ? <div className="empty-note">여기엔 아무거나 던져도 된다.<br />분류는 나중에.</div>
        : <div className="stickies">
            {rows.map((r, i) => (
              <div key={r.id} className="sticky" data-hue={i % 4}>
                <p>{r.body || r.title}</p>
                <div className="sticky-foot">
                  <span className="when">
                    {new Date(r.created_at).toLocaleDateString('ko-KR',
                      { month: 'numeric', day: 'numeric' })}
                  </span>
                  {isOwner && targets.length > 0 && (
                    <select defaultValue="" onChange={async e => {
                      if (!e.target.value) return
                      await api.moveEntry(r.id, e.target.value); await reload()
                    }}>
                      <option value="">어디로 →</option>
                      {targets.map(t => (
                        <option key={t.id} value={t.id}>{t.label} ({KIND_LABEL[t.kind]})</option>
                      ))}
                    </select>
                  )}
                  {isOwner && (
                    <button className="x" onClick={async () => {
                      await api.deleteEntry(r.id); await reload()
                    }}>×</button>
                  )}
                </div>
              </div>
            ))}
          </div>}
    </div>
  )
}
