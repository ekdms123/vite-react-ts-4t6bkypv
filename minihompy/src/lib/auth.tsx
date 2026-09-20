import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import type { Session } from '@supabase/supabase-js'
import { supabase } from './supabase'
import { getProfileById } from './api'
import type { Profile } from './types'

interface AuthValue {
  session: Session | null
  me: Profile | null
  loading: boolean
  refreshMe: () => Promise<void>
  signInGoogle: () => Promise<void>
  signUpEmail: (email: string, password: string) => Promise<string | null>
  signInEmail: (email: string, password: string) => Promise<string | null>
  signOut: () => Promise<void>
}

const Ctx = createContext<AuthValue>({
  session: null, me: null, loading: true,
  refreshMe: async () => {},
  signInGoogle: async () => {},
  signUpEmail: async () => null,
  signInEmail: async () => null,
  signOut: async () => {},
})

/** Supabase가 돌려주는 영어 오류를 그대로 보여주면 무슨 소린지 모른다. */
function readable(message: string): string {
  const m = message.toLowerCase()
  if (m.includes('invalid login credentials')) return '이메일이나 비밀번호가 틀렸다.'
  if (m.includes('already registered') || m.includes('already been registered'))
    return '이미 가입된 이메일이다. 로그인 쪽으로.'
  if (m.includes('password should be at least')) return '비밀번호는 6글자 이상이어야 한다.'
  if (m.includes('unable to validate email') || m.includes('invalid email'))
    return '이메일 모양이 아니다.'
  if (m.includes('email not confirmed'))
    return '메일함에서 인증 링크를 눌러야 한다. (Supabase에서 이메일 확인을 끄면 바로 된다)'
  if (m.includes('rate limit') || m.includes('too many'))
    return '잠깐 사이에 너무 많이 시도했다. 조금 뒤에 다시.'
  // 가입 명단에 없는 이메일은 데이터베이스가 거절한다. 그 예외가 여기로 온다.
  if (message.includes('초대받지 않은') || m.includes('database error saving new user'))
    return '초대된 이메일이 아니다. 집주인에게 명단에 넣어달라고 하면 된다.'
  return message
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [me, setMe] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)

  async function loadProfile(uid: string | undefined) {
    if (!uid) { setMe(null); return }
    // 가입 직후에는 트리거가 프로필을 만드는 사이 한 박자 비는 수가 있다.
    for (let attempt = 0; attempt < 3; attempt++) {
      const p = await getProfileById(uid)
      if (p) { setMe(p); return }
      await new Promise(r => setTimeout(r, 400))
    }
    setMe(null)
  }

  useEffect(() => {
    supabase.auth.getSession().then(async ({ data }) => {
      setSession(data.session)
      await loadProfile(data.session?.user.id)
      setLoading(false)
    })
    const { data: sub } = supabase.auth.onAuthStateChange(async (_e, s) => {
      setSession(s)
      await loadProfile(s?.user.id)
      setLoading(false)
    })
    return () => sub.subscription.unsubscribe()
  }, [])

  const value: AuthValue = {
    session, me, loading,
    refreshMe: () => loadProfile(session?.user.id),
    signInGoogle: async () => {
      await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: window.location.origin },
      })
    },
    signUpEmail: async (email, password) => {
      const { error } = await supabase.auth.signUp({ email, password })
      return error ? readable(error.message) : null
    },
    signInEmail: async (email, password) => {
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      return error ? readable(error.message) : null
    },
    signOut: async () => { await supabase.auth.signOut(); setMe(null) },
  }
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export const useAuth = () => useContext(Ctx)
