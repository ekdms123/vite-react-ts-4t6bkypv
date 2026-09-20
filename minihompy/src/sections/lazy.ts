import { lazy } from 'react'

/**
 * 탭마다 코드를 따로 받는다.
 *
 * 처음 열 때 열 개 탭의 코드를 전부 파싱하느라 느린 폰에서 한 탭 여는 데
 * 400ms 가 걸렸다. 쪼개면 첫 화면이 가벼워지지만, 탭을 눌렀을 때 그제야
 * 받으면 더 느려진다. 그래서 첫 화면이 그려지고 브라우저가 한가해진 순간
 * 나머지를 조용히 미리 받아둔다 — 사람이 탭을 누를 때쯤이면 이미 와 있다.
 */
export const Todo      = lazy(() => import('./Todo'))
export const Calendar  = lazy(() => import('./Calendar'))
export const Diary     = lazy(() => import('./Diary'))
export const Photos    = lazy(() => import('./Photos'))
export const Ledger    = lazy(() => import('./Ledger'))
export const Challenge = lazy(() => import('./Challenge'))
export const Jukebox   = lazy(() => import('./Jukebox'))
export const Inbox     = lazy(() => import('./Inbox'))

let warmed = false
export function warmSections() {
  if (warmed) return
  warmed = true
  const load = () => {
    void import('./Todo'); void import('./Calendar'); void import('./Diary')
    void import('./Photos'); void import('./Ledger'); void import('./Challenge')
    void import('./Jukebox'); void import('./Inbox')
  }
  if ('requestIdleCallback' in window) requestIdleCallback(load, { timeout: 2500 })
  else setTimeout(load, 1200)
}
