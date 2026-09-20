import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import type { Entry, Section } from '../lib/types'
import Editable from '../components/Editable'

const DAY = 86_400_000

function dday(due: string) {
  const d = Math.floor((new Date(due).setHours(0, 0, 0, 0) - new Date().setHours(0, 0, 0, 0)) / DAY)
  if (d === 0) return { text: '오늘', tone: 'now' as const }
  if (d < 0)   return { text: `${-d}일 지남`, tone: 'past' as const }
  return { text: `D-${d}`, tone: 'soon' as const }
}

/** 할 일 · 체크리스트 · 마감을 한 판에 둔다. 끝난 건 접어서 치운다. */
export default function Todo({ section, isOwner, uid }: {
  section: Section; isOwner: boolean; uid: string | null
}) {
  const [rows, setRows] = useState<Entry[]>([])
  const [text, setText] = useState('')
  const [due, setDue] = useState('')
  const [showDone, setShowDone] = useState(false)
  const [busy, setBusy] = useState(false)

  async function reload() { setRows(await api.listEntries(section.id)) }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [section.id])

  async function add() {
    if (!uid || !text.trim()) return
    setBusy(true)
    try {
      await api.createEntry({
        section_id: section.id, owner: uid,
        title: text.trim(),
        due_at: due ? new Date(due).toISOString() : null,
        visibility: section.visibility,
      })
      setText(''); setDue(''); await reload()
    } finally { setBusy(false) }
  }

  /**
   * 체크는 눌린 순간 화면에서 먼저 옮기고, 서버는 뒤따라간다.
   * 쓰기와 다시 읽기를 기다리면 폰에서 반 박자씩 멍해지는데, 그 반 박자가
   * 쌓이면 체크 자체를 안 하게 된다. 실패하면 제자리로 돌려놓는다.
   */
  async function flip(row: Entry, next: boolean) {
    setRows(rs => rs.map(r => (r.id === row.id ? { ...r, done: next } : r)))
    try { await api.toggleDone(row.id, next) }
    catch (e) {
      setRows(rs => rs.map(r => (r.id === row.id ? { ...r, done: !next } : r)))
      throw e
    }
  }

  async function drop(row: Entry) {
    setRows(rs => rs.filter(r => r.id !== row.id))
    try { await api.deleteEntry(row.id) }
    catch (e) { await reload(); throw e }
  }

  const open = rows.filter(r => !r.done)
  const done = rows.filter(r => r.done)

  return (
    <div>
      <div className="sec-title">
        {section.label}
        <span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>
          {open.length}개 남음
        </span>
      </div>

      {isOwner && (
        <div className="quick-add">
          <input type="text" placeholder="할 일 한 줄" value={text}
                 onChange={e => setText(e.target.value)}
                 onKeyDown={e => { if (e.key === 'Enter') void add() }} />
          <input type="date" value={due} onChange={e => setDue(e.target.value)}
                 title="마감 (없어도 됨)" style={{ width: 126 }} />
          <button className="btn" onClick={add} disabled={busy || !text.trim()}>담기</button>
        </div>
      )}

      {open.length === 0
        ? <div className="empty-note">오늘은 비어 있다.<br />하나만 적어도 충분하다.</div>
        : <ul className="checklist">
            {open.map(r => {
              const d = r.due_at ? dday(r.due_at) : null
              return (
                <li key={r.id}>
                  <button className="tick" aria-label="완료"
                          onClick={() => flip(r, true)} disabled={!isOwner} />
                  <Editable className="what" value={r.title} disabled={!isOwner}
                            onSave={async next => {
                              await api.updateEntry(r.id, { title: next }); await reload()
                            }} />
                  {d && <span className={`dday ${d.tone}`}>{d.text}</span>}
                  {isOwner && (
                    <button className="x" title="지우기"
                            onClick={() => drop(r)}>×</button>
                  )}
                </li>
              )
            })}
          </ul>}

      {done.length > 0 && (
        <div style={{ marginTop: 14 }}>
          <button className="fold" onClick={() => setShowDone(v => !v)}>
            {showDone ? '▾' : '▸'} 끝낸 것 {done.length}
          </button>
          {showDone && (
            <ul className="checklist done">
              {done.map(r => (
                <li key={r.id}>
                  <button className="tick on" aria-label="되돌리기"
                          onClick={() => flip(r, false)} disabled={!isOwner} />
                  <span className="what">{r.title}</span>
                  {isOwner && (
                    <button className="x"
                            onClick={() => drop(r)}>×</button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
