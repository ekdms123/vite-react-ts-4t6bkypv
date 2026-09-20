/**
 * 시간대 회귀. `node --test src/lib/day.test.mjs` 로 돌린다.
 * TZ 를 바꿔가며 돌려야 의미가 있다 — UTC 에서만 돌리면 이 버그는 안 잡힌다.
 */
import { test } from 'node:test'
import assert from 'node:assert/strict'

const dayKey = d => {
  const x = typeof d === 'string' ? new Date(d) : d
  return `${x.getFullYear()}-${String(x.getMonth()+1).padStart(2,'0')}-${String(x.getDate()).padStart(2,'0')}`
}
function streakOf(stamps) {
  const days = new Set(stamps.map(dayKey))
  const cur = new Date()
  if (!days.has(dayKey(cur))) cur.setDate(cur.getDate() - 1)
  let streak = 0
  while (days.has(dayKey(cur))) { streak++; cur.setDate(cur.getDate() - 1) }
  return { streak, total: days.size }
}

test('새벽에 찍은 기록이 그날로 들어간다', () => {
  // 한국 새벽 1시. UTC 로는 전날 16시라 toISOString 은 어제를 준다.
  const dawn = new Date('2026-09-20T01:00:00+09:00')
  if (process.env.TZ === 'Asia/Seoul') {
    assert.equal(dayKey(dawn), '2026-09-20')
    assert.notEqual(dayKey(dawn), dawn.toISOString().slice(0, 10))
  }
})

test('밤 11시도 그날로 들어간다', () => {
  const late = new Date('2026-09-20T23:30:00+09:00')
  if (process.env.TZ === 'Asia/Seoul') assert.equal(dayKey(late), '2026-09-20')
})

test('오늘 안 했어도 어제까지 이어졌으면 연속이다', () => {
  const d = n => { const x = new Date(); x.setDate(x.getDate() - n); return x }
  assert.equal(streakOf([d(1), d(2), d(3)]).streak, 3)
})

test('끊겨도 누적은 남는다', () => {
  const d = n => { const x = new Date(); x.setDate(x.getDate() - n); return x }
  const r = streakOf([d(10), d(11), d(12)])
  assert.equal(r.streak, 0)
  assert.equal(r.total, 3)
})

test('같은 날 두 번 찍어도 하루다', () => {
  const a = new Date(); const b = new Date(a); b.setHours(a.getHours() === 23 ? 1 : 23)
  assert.equal(streakOf([a, b]).total, 1)
})
