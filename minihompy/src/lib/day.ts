/**
 * 날짜는 사는 곳의 자정으로 끊는다.
 *
 * `toISOString().slice(0,10)` 은 UTC 날짜를 준다. 한국에서 새벽 한 시에
 * 챌린지를 체크하면 UTC로는 아직 전날이라 그 기록이 어제로 들어갔고,
 * 아침에 분명히 눌렀는데 연속이 안 늘어나는 것처럼 보였다.
 * 사람이 하루라고 느끼는 경계는 자기가 서 있는 곳의 자정이다.
 */

export function dayKey(d: Date | string): string {
  const x = typeof d === 'string' ? new Date(d) : d
  const y = x.getFullYear()
  const m = String(x.getMonth() + 1).padStart(2, '0')
  const day = String(x.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export const todayKey = () => dayKey(new Date())

/** 오늘 자정부터 n일 전/후의 날짜 문자열. */
export function shiftDay(n: number, from = new Date()): string {
  const d = new Date(from)
  d.setDate(d.getDate() + n)
  return dayKey(d)
}

/**
 * 연속과 누적을 따로 센다. 하루 빠졌다고 누적까지 0으로 돌리면
 * 한 번 끊긴 사람은 다시 오지 않는다. 끊기는 건 연속뿐이다.
 */
export function streakOf(stamps: Array<Date | string>) {
  const days = new Set(stamps.map(dayKey))
  const cur = new Date()
  // 오늘 아직 안 했을 수 있으니, 어제부터 이어져 있으면 연속으로 친다.
  if (!days.has(dayKey(cur))) cur.setDate(cur.getDate() - 1)
  let streak = 0
  while (days.has(dayKey(cur))) { streak++; cur.setDate(cur.getDate() - 1) }
  return { streak, total: days.size }
}
