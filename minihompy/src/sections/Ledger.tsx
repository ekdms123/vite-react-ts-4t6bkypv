import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import { INCOME_CATEGORIES, LEDGER_CATEGORIES, type Section } from '../lib/types'
import Editable from '../components/Editable'
import type { Entry } from '../lib/types'

const won = (n: number) => n.toLocaleString('ko-KR') + '원'
type Stats = Awaited<ReturnType<typeof api.moneyStats>>

/**
 * 합계 하나만 크게 띄우면 가계부는 영수증 더미가 된다. 지난달과 나란히
 * 놓고, 어느 날 몰아 썼는지 보여주고, 예산과 벌어진 자리를 짚어야
 * 다음 달에 바꿀 게 생긴다.
 */
export default function Ledger({ section, isOwner, uid }: {
  section: Section; isOwner: boolean; uid: string | null
}) {
  const [month, setMonth] = useState(() => new Date())
  const [d, setD] = useState<Stats | null>(null)
  const [amount, setAmount] = useState('')
  const [title, setTitle] = useState('')
  const [income, setIncome] = useState(false)
  const [cat, setCat] = useState(LEDGER_CATEGORIES[0])
  const [planned, setPlanned] = useState(false)
  const [busy, setBusy] = useState(false)

  async function reload() { setD(await api.moneyStats(section.id, month)) }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [section.id, month])
  useEffect(() => { setCat((income ? INCOME_CATEGORIES : LEDGER_CATEGORIES)[0]) }, [income])

  async function add() {
    const n = Number(amount.replace(/[^0-9]/g, ''))
    if (!uid || !n) return
    setBusy(true)
    try {
      await api.createEntry({
        section_id: section.id, owner: uid,
        title: title.trim() || cat, amount: n, category: cat,
        is_planned: planned && !income, is_income: income,
        visibility: section.visibility,
      })
      setAmount(''); setTitle(''); await reload()
    } finally { setBusy(false) }
  }

  const shift = (n: number) =>
    setMonth(m => new Date(m.getFullYear(), m.getMonth() + n, 1))

  if (!d) return <div className="empty-note">불러오는 중…</div>

  const diff = d.spent - d.prev
  const left = d.planned - d.spent
  const pct  = d.planned > 0 ? Math.min(100, Math.round((d.spent / d.planned) * 100)) : 0
  const peak = Math.max(...d.daily, 1)
  const cats = Object.entries(d.byCategory).sort((a, b) => b[1] - a[1])

  return (
    <div>
      <div className="sec-title cal-head">
        <button className="nav" aria-label="지난달" onClick={() => shift(-1)}>‹</button>
        <span>{month.getFullYear()}년 {month.getMonth() + 1}월</span>
        <button className="nav" aria-label="다음달" onClick={() => shift(1)}>›</button>
      </div>

      {/* 세 숫자를 한 줄에. 쓴 돈만 있으면 많고 적음을 알 수 없다. */}
      <div className="money-grid">
        <div className="mcell out">
          <span className="k">썼다</span>
          <b>{won(d.spent)}</b>
          {d.prev > 0 && (
            <em data-up={diff > 0}>
              지난달보다 {diff === 0 ? '같음' : `${won(Math.abs(diff))} ${diff > 0 ? '더' : '덜'}`}
            </em>
          )}
        </div>
        <div className="mcell in">
          <span className="k">들어왔다</span>
          <b>{won(d.income)}</b>
        </div>
        <div className="mcell net">
          <span className="k">남았다</span>
          <b data-neg={d.income - d.spent < 0}>{won(d.income - d.spent)}</b>
        </div>
      </div>

      {d.planned > 0 && (
        <div className="budget">
          <div className="bar"><i style={{ width: `${pct}%` }} data-over={pct >= 100} /></div>
          <div className="k">
            예산 {won(d.planned)} 중 {pct}% ·{' '}
            {left >= 0 ? `${won(left)} 남음` : `${won(-left)} 넘음`}
          </div>
        </div>
      )}

      {/* 일별 추이 — 어느 날 몰아 썼는지가 카테고리 합계보다 자주 답이다 */}
      {d.spent > 0 && (
        <div className="spark" role="img" aria-label="일별 지출">
          {d.daily.map((v, i) => (
            <i key={i} style={{ height: `${Math.max(2, (v / peak) * 100)}%` }}
               data-has={v > 0} title={`${i + 1}일 ${won(v)}`} />
          ))}
        </div>
      )}

      {isOwner && (
        <div className="quick-add money">
          <div className="io">
            <button data-on={!income} onClick={() => setIncome(false)}>지출</button>
            <button data-on={income} onClick={() => setIncome(true)}>수입</button>
          </div>
          <input type="text" inputMode="numeric" placeholder="금액" value={amount}
                 onChange={e => setAmount(e.target.value)}
                 onKeyDown={e => { if (e.key === 'Enter') void add() }} style={{ width: 88 }} />
          <select value={cat} onChange={e => setCat(e.target.value)}
                  aria-label="분류" style={{ width: 84 }}>
            {(income ? INCOME_CATEGORIES : LEDGER_CATEGORIES).map(c => <option key={c}>{c}</option>)}
          </select>
          <input type="text" placeholder="뭐에 썼나 (생략 가능)" value={title}
                 onChange={e => setTitle(e.target.value)} />
          {!income && (
            <label className="tiny">
              <input type="checkbox" checked={planned} style={{ width: 'auto' }}
                     onChange={e => setPlanned(e.target.checked)} />
              예산
            </label>
          )}
          <button className="btn" onClick={add} disabled={busy || !amount}>담기</button>
        </div>
      )}

      {d.biggest && (
        <div className="biggest">
          이번 달 제일 큰 지출 — <b>{d.biggest.title}</b> {won(d.biggest.amount ?? 0)}
        </div>
      )}

      {cats.length > 0 && (
        <div className="cat-rows">
          {cats.map(([k, v]) => (
            <div key={k} className="cat-row">
              <span className="chip">{k}</span>
              <i style={{ width: `${Math.round((v / d.spent) * 100)}%` }} />
              <b>{won(v)}</b>
              <em className="pctl">{Math.round((v / d.spent) * 100)}%</em>
            </div>
          ))}
        </div>
      )}

      {d.rows.length === 0
        ? <div className="empty-note">이번 달 기록이 없다.</div>
        : byDay(d.rows.filter(r => !r.is_planned)).map(([day, items, sum]) => (
          <div key={day} className="day-group">
            <div className="day-rule">
              <span>{day}일</span>
              <i>{sum >= 0 ? '−' : '+'}{won(Math.abs(sum))}</i>
            </div>
            <ul className="ledger-list">
            {items.map(r => (
              <li key={r.id} data-income={r.is_income}>
                <span className="chip">{r.category}</span>
                <Editable className="what" value={r.title} disabled={!isOwner}
                          onSave={async next => {
                            await api.updateEntry(r.id, { title: next }); await reload()
                          }} />
                <b>{r.is_income ? '+' : '−'}{won(r.amount ?? 0)}</b>
                <span className="when">{new Date(r.created_at).getDate()}일</span>
                {isOwner && (
                  <button className="x" aria-label="지우기" onClick={async () => {
                    await api.deleteEntry(r.id); await reload()
                  }}>×</button>
                )}
              </li>
            ))}
            </ul>
          </div>
        ))}
    </div>
  )
}

/** 거래를 날짜별로 묶고 그날 쓴 합을 붙인다. 하루 단위가 사람이 기억하는 단위다. */
function byDay(rows: Entry[]): [number, Entry[], number][] {
  const m = new Map<number, Entry[]>()
  for (const r of rows) {
    const d = new Date(r.created_at).getDate()
    const list = m.get(d); list ? list.push(r) : m.set(d, [r])
  }
  return [...m.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([d, items]) => [d, items,
      items.reduce((s, r) => s + (r.is_income ? -(r.amount ?? 0) : (r.amount ?? 0)), 0)])
}
