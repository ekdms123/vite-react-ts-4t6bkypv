import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'

type Kind = 'ok' | 'bad'
interface Note { id: number; kind: Kind; text: string }

const Ctx = createContext<{ say: (text: string, kind?: Kind) => void }>({ say: () => {} })

/** Supabase가 돌려주는 영어를 그대로 띄우면 무슨 소린지 모른다. */
function readable(e: unknown): string {
  const raw = e instanceof Error ? e.message : String(e ?? '')
  const m = raw.toLowerCase()
  if (m.includes('failed to fetch') || m.includes('networkerror'))
    return '인터넷이 끊긴 것 같다. 잠시 뒤에 다시.'
  if (m.includes('row-level security') || m.includes('permission'))
    return '권한이 없다. 남의 것은 못 고친다.'
  if (m.includes('duplicate key') && m.includes('handle'))
    return '이미 쓰는 주소다.'
  if (m.includes('duplicate key')) return '이미 있는 것이다.'
  if (m.includes('payload too large') || m.includes('exceeded the maximum'))
    return '파일이 너무 크다. 작은 사진으로 다시.'
  if (m.includes('storage') && m.includes('quota')) return '저장 공간이 찼다.'
  if (m.includes('jwt') || m.includes('not authenticated'))
    return '로그인이 풀렸다. 새로고침하고 다시 들어가야 한다.'
  return raw || '뭔가 잘못됐다.'
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [notes, setNotes] = useState<Note[]>([])

  const say = useCallback((text: string, kind: Kind = 'ok') => {
    const id = Date.now() + Math.random()
    setNotes(n => [...n, { id, kind, text }])
    setTimeout(() => setNotes(n => n.filter(x => x.id !== id)), kind === 'bad' ? 5200 : 2600)
  }, [])

  /**
   * 화면마다 try/catch를 다는 대신 여기서 한 번에 받는다. 대부분의 호출은
   * `void reload()` 꼴이라 실패해도 아무 일도 일어나지 않았는데, 사용자
   * 입장에서 그건 버튼이 고장난 것과 구별되지 않는다.
   */
  useEffect(() => {
    const onReject = (e: PromiseRejectionEvent) => { say(readable(e.reason), 'bad') }
    const onError = (e: ErrorEvent) => { say(readable(e.error ?? e.message), 'bad') }
    addEventListener('unhandledrejection', onReject)
    addEventListener('error', onError)
    return () => {
      removeEventListener('unhandledrejection', onReject)
      removeEventListener('error', onError)
    }
  }, [say])

  return (
    <Ctx.Provider value={{ say }}>
      {children}
      <div className="toasts" role="status" aria-live="polite">
        {notes.map(n => <div key={n.id} className="toast" data-kind={n.kind}>{n.text}</div>)}
      </div>
    </Ctx.Provider>
  )
}

export const useToast = () => useContext(Ctx)
