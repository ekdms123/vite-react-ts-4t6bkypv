import { useEffect, useMemo, useState } from 'react'
import * as api from '../lib/api'
import type { Entry, Section } from '../lib/types'
import { dayKey } from '../lib/day'

const DAY = 86_400_000


/**
 * 연속일만 보여주는 트래커는 한 번 끊긴 사람을 돌려보낸다.
 * 끊기는 건 연속뿐이고 누적은 그대로 남는다는 걸 화면이 말해야 한다.
 */
export default function Challenge({ section, isOwner, uid }: {
  section: Section; isOwner: boolean; uid: string | null
}) {
  const [rows, setRows] = useState<Entry[]>([])
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)

  async function reload() { setRows(await api.challengeLog(section.id)) }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [section.id])

  /** 같은 이름끼리 묶는다. category 칸을 챌린지 이름으로 쓴다. */
  const groups = useMemo(() => {
    const m = new Map<string, Entry[]>()
    for (const r of rows) {
      const k = r.category || r.title || '무제'
      const list = m.get(k); list ? list.push(r) : m.set(k, [r])
    }
    return [...m.entries()]
  }, [rows])

  async function check(label: string) {
    if (!uid) return
    setBusy(true)
    try {
      await api.createEntry({
        section_id: section.id, owner: uid,
        title: label, category: label, visibility: section.visibility,
      })
      await reload()
    } finally { setBusy(false) }
  }

  async function addChallenge() {
    if (!name.trim()) return
    await check(name.trim()); setName('')
  }

  const today = dayKey(new Date())

  return (
    <div>
      <div className="sec-title">{section.label}</div>

      {isOwner && (
        <div className="quick-add">
          <input type="text" placeholder="새 챌린지 이름 (예: 물 마시기)" value={name}
                 onChange={e => setName(e.target.value)}
                 onKeyDown={e => { if (e.key === 'Enter') void addChallenge() }} />
          <button className="btn" onClick={addChallenge} disabled={busy || !name.trim()}>
            시작
          </button>
        </div>
      )}

      {groups.length === 0
        ? <div className="empty-note">아직 챌린지가 없다.<br />작은 걸로 하나만.</div>
        : groups.map(([label, list]) => {
            const dates = list.map(r => r.created_at)
            const { streak, total } = api.streakOf(dates)
            const doneToday = dates.some(d => d.slice(0, 10) === today)
            const days = new Set(dates.map(d => d.slice(0, 10)))
            // 지난 5주. 빈 칸도 그대로 둔다 — 비어 있는 게 실패는 아니다.
            const cells = Array.from({ length: 35 }, (_, i) => {
              const d = new Date(Date.now() - (34 - i) * DAY)
              return { k: dayKey(d), on: days.has(dayKey(d)), today: dayKey(d) === today }
            })
            return (
              <div key={label} className="challenge">
                <div className="ch-head">
                  <b>{label}</b>
                  <span className="k">연속 {streak}일 · 누적 {total}일</span>
                  {isOwner && (
                    <button className={`btn ${doneToday ? 'ghost' : ''}`}
                            onClick={() => check(label)} disabled={busy}>
                      {doneToday ? '오늘 했음' : '오늘 하기'}
                    </button>
                  )}
                </div>
                <div className="grass">
                  {cells.map(c => (
                    <i key={c.k} data-on={c.on} data-today={c.today} title={c.k} />
                  ))}
                </div>
                {streak === 0 && total > 0 && (
                  <div className="k soft">끊겼어도 {total}일은 그대로 남아 있다.</div>
                )}
              </div>
            )
          })}
    </div>
  )
}
