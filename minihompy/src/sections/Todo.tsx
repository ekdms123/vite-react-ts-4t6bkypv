import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import type { Entry, Section } from '../lib/types'
import Editable from '../components/Editable'

const DAY = 86_400_000

function daysUntil(due: string) {
  return Math.floor((new Date(due).setHours(0, 0, 0, 0) - new Date().setHours(0, 0, 0, 0)) / DAY)
}

function dday(due: string) {
  const d = daysUntil(due)
  if (d === 0) return { text: '오늘', tone: 'now' as const }
  if (d < 0)   return { text: `${-d}일 지남`, tone: 'past' as const }
  return { text: `D-${d}`, tone: 'soon' as const }
}

/**
 * 마흔 개가 한 줄로 늘어서 있으면 사람은 첫 줄도 시작하지 않는다.
 * 무엇부터 할지 고르는 일까지 떠안기기 때문이다. 그래서 목록이 먼저
 * 나눠 들고, 각 묶음은 지금 손댈 만한 크기로만 열려 있는다.
 */
const BUCKETS = [
  { key: 'past',   label: '지났다',     open: true,  hint: '오늘로 당기거나 지워도 된다' },
  { key: 'today',  label: '오늘',       open: true,  hint: '' },
  { key: 'week',   label: '이번 주',    open: true,  hint: '' },
  { key: 'later',  label: '나중에',     open: false, hint: '' },
  { key: 'someday',label: '언젠가',     open: false, hint: '날짜를 안 정한 것들' },
] as const
type BucketKey = typeof BUCKETS[number]['key']

function bucketOf(r: Entry): BucketKey {
  if (!r.due_at) return 'someday'
  const d = daysUntil(r.due_at)
  if (d < 0) return 'past'
  if (d === 0) return 'today'
  if (d <= 7) return 'week'
  return 'later'
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

  /** 오늘로 당기기 — 지난 것을 지우지 않고 다시 살리는 한 번의 동작. */
  async function pullToToday(row: Entry) {
    const t = new Date(); t.setHours(23, 59, 0, 0)
    setRows(rs => rs.map(r => (r.id === row.id ? { ...r, due_at: t.toISOString() } : r)))
    try { await api.updateEntry(row.id, { due_at: t.toISOString() }) }
    catch (e) { await reload(); throw e }
  }

  const open = rows.filter(r => !r.done)
  const done = rows.filter(r => r.done)
  const groups = BUCKETS.map(b => ({
    ...b, items: open.filter(r => bucketOf(r) === b.key),
  })).filter(g => g.items.length > 0)

  return (
    <div>
      <div className="sec-title">
        {section.label}
        <span style={{ float: 'right', fontWeight: 400, color: '#636363' }}>
          {open.length}개 남음
        </span>
      </div>

      {isOwner && (
        <div className="quick-add">
          <input type="text" placeholder="할 일 한 줄" value={text}
                 onChange={e => setText(e.target.value)}
                 onKeyDown={e => { if (e.key === 'Enter') void add() }} />
          <input type="date" value={due} onChange={e => setDue(e.target.value)}
                 aria-label="마감 날짜 (없어도 됨)" style={{ width: 126 }} />
          <button className="btn" onClick={add} disabled={busy || !text.trim()}>담기</button>
        </div>
      )}

      {open.length === 0
        ? <div className="empty-note">오늘은 비어 있다.<br />하나만 적어도 충분하다.</div>
        : groups.map(g => (
            <details key={g.key} className="bucket" open={g.open} data-tone={g.key}>
              <summary>
                <span className="b-label">{g.label}</span>
                <span className="b-count">{g.items.length}</span>
                {g.hint && <span className="b-hint">{g.hint}</span>}
              </summary>
              <ul className="checklist">
                {g.items.map(r => {
                  const d = r.due_at ? dday(r.due_at) : null
                  return (
                    <li key={r.id}>
                      <button className="tick" aria-label="다 했음으로 표시"
                              onClick={() => flip(r, true)} disabled={!isOwner} />
                      <Editable className="what" value={r.title} disabled={!isOwner}
                                onSave={async next => {
                                  await api.updateEntry(r.id, { title: next }); await reload()
                                }} />
                      {g.key === 'past' && isOwner && (
                        <button className="crumb pull-today" onClick={() => pullToToday(r)}>
                          오늘로
                        </button>
                      )}
                      {d && <span className={`dday ${d.tone}`}>{d.text}</span>}
                      {isOwner && (
                        <button className="x" aria-label="지우기" title="지우기"
                                onClick={() => drop(r)}>×</button>
                      )}
                    </li>
                  )
                })}
              </ul>
            </details>
          ))}

      {done.length > 0 && (
        <div style={{ marginTop: 14 }}>
          <button className="fold" aria-expanded={showDone} onClick={() => setShowDone(v => !v)}>
            {showDone ? '▾' : '▸'} 끝낸 것 {done.length}
          </button>
          {showDone && (
            <ul className="checklist done">
              {done.map(r => (
                <li key={r.id}>
                  <button className="tick on" aria-label="아직 안 한 것으로 되돌리기"
                          onClick={() => flip(r, false)} disabled={!isOwner} />
                  <span className="what">{r.title}</span>
                  {isOwner && (
                    <button className="x" aria-label="지우기"
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
