import { useEffect, useRef, useState } from 'react'
import * as api from '../lib/api'
import type { Entry, Profile, SectionKind } from '../lib/types'

type Hit = Entry & { sections: { label: string; kind: SectionKind } }

/** 어디에 적었는지 기억 안 날 때 쓰는 곳. */
export default function Search({ me, onJump, onClose }: {
  me: Profile; onJump: (sectionId: string) => void; onClose: () => void
}) {
  const [q, setQ] = useState('')
  const [hits, setHits] = useState<Hit[]>([])
  const [busy, setBusy] = useState(false)
  const box = useRef<HTMLInputElement>(null)

  useEffect(() => { box.current?.focus() }, [])
  useEffect(() => {
    if (!q.trim()) { setHits([]); return }
    // 한 글자 칠 때마다 찌르지 않는다
    const t = setTimeout(async () => {
      setBusy(true)
      try { setHits(await api.searchAll(me.id, q)) } finally { setBusy(false) }
    }, 220)
    return () => clearTimeout(t)
  }, [q, me.id])

  return (
    <div className="sheet">
      <div className="sheet-head">
        <b>찾기</b>
        <button className="btn ghost" onClick={onClose}>닫기</button>
      </div>
      <input ref={box} type="text" placeholder="뭐든 한 조각만 기억나면"
             value={q} onChange={e => setQ(e.target.value)}
             onKeyDown={e => { if (e.key === 'Escape') onClose() }} />

      {!q.trim()
        ? <div className="empty-note">일기든 일정이든 가계부든 한 번에 찾는다.</div>
        : busy
          ? <div className="empty-note">찾는 중…</div>
          : hits.length === 0
            ? <div className="empty-note">없다.<br />다른 말로 해보자.</div>
            : <div className="hits">
                {hits.map(h => (
                  <button key={h.id} className="hit"
                          onClick={() => { onJump(h.section_id); onClose() }}>
                    <span className="chip">{h.sections?.label}</span>
                    <span className="hit-text">
                      <b>{h.title || '(제목 없음)'}</b>
                      {h.body && <em>{h.body.slice(0, 60)}</em>}
                    </span>
                    <span className="when">
                      {new Date(h.created_at).toLocaleDateString('ko-KR',
                        { year: '2-digit', month: 'numeric', day: 'numeric' })}
                    </span>
                  </button>
                ))}
              </div>}
    </div>
  )
}
