import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import { ENERGY, type EnergyKey, type Entry, type Profile, type Section } from '../lib/types'

type Loaded = {
  todos: (Entry & { sections: { label: string } })[]
  due: (Entry & { sections: { label: string } })[]
  recent: Awaited<ReturnType<typeof api.recentEntries>>
  counts: Record<string, number>
}

/**
 * 대문. 오늘 할 것과 던지는 칸만 있으면 된다.
 * 목록 전체를 보여주면 아무것도 안 하게 되므로 에너지만큼만 자른다.
 */
export default function HomePanel({ profile, sections, isOwner, uid, energy, onJump }: {
  profile: Profile
  sections: Section[]
  isOwner: boolean
  uid: string | null
  energy: EnergyKey
  onJump: (sectionId: string) => void
}) {
  const [d, setD] = useState<Loaded | null>(null)
  const [note, setNote] = useState('')
  const [saved, setSaved] = useState(false)

  async function reload() {
    const [todos, due, recent, counts] = await Promise.all([
      api.openTodos(profile.id),
      api.dueSoon(profile.id),
      api.recentEntries(profile.id, 5),
      api.countsBySection(profile.id),
    ])
    setD({ todos, due, recent, counts })
  }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [profile.id])

  const topN = ENERGY.find(e => e.key === energy)?.topN ?? 3

  async function capture() {
    if (!uid || !note.trim()) return
    await api.captureTo(uid, sections, note)
    setNote(''); setSaved(true); setTimeout(() => setSaved(false), 1600)
    await reload()
  }

  if (!d) return <div className="empty-note">불러오는 중…</div>

  const top = d.todos.slice(0, topN)
  const rest = d.todos.length - top.length

  return (
    <div className="home">
      {isOwner && (
        <section className="block capture">
          <div className="news-title">지금 떠오른 것</div>
          <textarea rows={2} value={note} placeholder="아무거나. 분류는 나중에."
                    onChange={e => setNote(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) void capture()
                    }} />
          <div className="capture-foot">
            <span className="k">{saved ? '보관함에 넣었다' : '⌘/Ctrl + Enter'}</span>
            <button className="btn" onClick={capture} disabled={!note.trim()}>던지기</button>
          </div>
        </section>
      )}

      <section className="block">
        <div className="news-title">오늘</div>
        {top.length === 0
          ? <div className="empty-note" style={{ padding: '18px 8px' }}>
              오늘은 비어 있다.<br />그래도 괜찮다.
            </div>
          : <ul className="checklist">
              {top.map(t => (
                <li key={t.id}>
                  <button className="tick" aria-label="완료" disabled={!isOwner}
                          onClick={async () => { await api.toggleDone(t.id, true); await reload() }} />
                  <span className="what">{t.title}</span>
                </li>
              ))}
            </ul>}
        {rest > 0 && (
          <div className="k soft">
            {rest}개는 접어뒀다. {energy === 'low' ? '오늘은 이만큼만.' : ''}
          </div>
        )}
      </section>

      {d.due.length > 0 && (
        <section className="block">
          <div className="news-title">곧 마감</div>
          <ul className="due-list">
            {d.due.map(t => (
              <li key={t.id}>
                <span className="chip">{t.sections?.label}</span>
                <span className="what">{t.title}</span>
                <b>{new Date(t.due_at!).toLocaleDateString('ko-KR',
                  { month: 'numeric', day: 'numeric' })}</b>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="block">
        <div className="news-title">Updated news</div>
        {d.recent.length === 0
          ? <div className="empty-note" style={{ padding: '14px 8px' }}>아직 소식이 없다.</div>
          : d.recent.map(r => (
              <div key={r.id} className="news-row">
                <span className="chip">{r.sections?.label}</span>
                <span className="what">{r.title || '(제목 없음)'}</span>
                <span className="when">
                  {new Date(r.created_at).toLocaleDateString('ko-KR',
                    { month: 'numeric', day: 'numeric' })}
                </span>
              </div>
            ))}

        <div className="counts">
          {sections.map(s => (
            <button key={s.id} className="count-cell" onClick={() => onJump(s.id)}>
              <span className="k">{s.label}</span>
              <span className="v">{d.counts[s.id] ?? 0}</span>
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}
