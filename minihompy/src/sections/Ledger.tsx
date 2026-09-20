import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import { LEDGER_CATEGORIES, type Section } from '../lib/types'

const won = (n: number) => n.toLocaleString('ko-KR') + '원'

/**
 * 합계만 보여주면 가계부는 영수증 더미가 된다. 쓸 생각이던 돈과
 * 실제로 쓴 돈을 나란히 놓아야 "어디서 어긋났나"를 물어볼 수 있다.
 */
export default function Ledger({ section, isOwner, uid }: {
  section: Section; isOwner: boolean; uid: string | null
}) {
  const [month] = useState(new Date())
  const [data, setData] = useState<Awaited<ReturnType<typeof api.monthMoney>> | null>(null)
  const [amount, setAmount] = useState('')
  const [title, setTitle] = useState('')
  const [cat, setCat] = useState(LEDGER_CATEGORIES[0])
  const [planned, setPlanned] = useState(false)
  const [busy, setBusy] = useState(false)

  async function reload() { setData(await api.monthMoney(section.id, month)) }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [section.id])

  async function add() {
    const n = Number(amount.replace(/[^0-9]/g, ''))
    if (!uid || !n) return
    setBusy(true)
    try {
      await api.createEntry({
        section_id: section.id, owner: uid,
        title: title.trim() || cat, amount: n, category: cat,
        is_planned: planned, visibility: section.visibility,
      })
      setAmount(''); setTitle(''); await reload()
    } finally { setBusy(false) }
  }

  const gap = data ? data.planned - data.spent : 0
  const pct = data && data.planned > 0
    ? Math.min(100, Math.round((data.spent / data.planned) * 100)) : 0

  return (
    <div>
      <div className="sec-title">
        {section.label}
        <span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>
          {month.getMonth() + 1}월
        </span>
      </div>

      {data && (
        <div className="money-head">
          <div className="big">
            <span className="k">썼다</span>
            <b>{won(data.spent)}</b>
          </div>
          {data.planned > 0 && (
            <>
              <div className="bar"><i style={{ width: `${pct}%` }} data-over={pct >= 100} /></div>
              <div className="k">
                예산 {won(data.planned)} 중 {pct}%
                {' · '}
                {gap >= 0 ? `${won(gap)} 남음` : `${won(-gap)} 넘음`}
              </div>
            </>
          )}
        </div>
      )}

      {isOwner && (
        <div className="quick-add money">
          <input type="text" inputMode="numeric" placeholder="금액" value={amount}
                 onChange={e => setAmount(e.target.value)}
                 onKeyDown={e => { if (e.key === 'Enter') void add() }} style={{ width: 92 }} />
          <select value={cat} onChange={e => setCat(e.target.value)} style={{ width: 88 }}>
            {LEDGER_CATEGORIES.map(c => <option key={c}>{c}</option>)}
          </select>
          <input type="text" placeholder="뭐에 썼나 (생략 가능)" value={title}
                 onChange={e => setTitle(e.target.value)} />
          <label className="tiny">
            <input type="checkbox" checked={planned} style={{ width: 'auto' }}
                   onChange={e => setPlanned(e.target.checked)} />
            예산
          </label>
          <button className="btn" onClick={add} disabled={busy || !amount}>담기</button>
        </div>
      )}

      {data && Object.keys(data.byCategory).length > 0 && (
        <div className="cat-rows">
          {Object.entries(data.byCategory).sort((a, b) => b[1] - a[1]).map(([k, v]) => (
            <div key={k} className="cat-row">
              <span className="chip">{k}</span>
              <i style={{ width: `${Math.round((v / data.spent) * 100)}%` }} />
              <b>{won(v)}</b>
            </div>
          ))}
        </div>
      )}

      {!data || data.rows.length === 0
        ? <div className="empty-note">이번 달 기록이 없다.</div>
        : <ul className="ledger-list">
            {data.rows.filter(r => !r.is_planned).map(r => (
              <li key={r.id}>
                <span className="chip">{r.category}</span>
                <span className="what">{r.title}</span>
                <b>{won(r.amount ?? 0)}</b>
                <span className="when">{new Date(r.created_at).getDate()}일</span>
                {isOwner && (
                  <button className="x"
                          onClick={async () => { await api.deleteEntry(r.id); await reload() }}>×</button>
                )}
              </li>
            ))}
          </ul>}
    </div>
  )
}
