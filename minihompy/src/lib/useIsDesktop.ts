import { useEffect, useState } from 'react'

/**
 * 레이아웃이 두 벌이라 분기 지점이 하나 필요하다. CSS로 못 감추는
 * 차이(펼침 대 접힘)만 여기로 가르고, 나머지 모양은 전부 CSS가 맡는다.
 */
export function useIsDesktop(breakpoint = 760) {
  const q = `(min-width: ${breakpoint + 1}px)`
  const [isDesktop, setIsDesktop] = useState(
    () => typeof window !== 'undefined' && window.matchMedia(q).matches,
  )
  useEffect(() => {
    const mql = window.matchMedia(q)
    const on = (e: MediaQueryListEvent) => setIsDesktop(e.matches)
    mql.addEventListener('change', on)
    setIsDesktop(mql.matches)
    return () => mql.removeEventListener('change', on)
  }, [q])
  return isDesktop
}
