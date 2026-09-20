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
  signIn: () => Promise<void>
  signOut: () => Promise<void>
}

const Ctx = createContext<AuthValue>({
  session: null, me: null, loading: true,
  refreshMe: async () => {}, signIn: async () => {}, signOut: async () => {},
})

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
    signIn: async () => {
      await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: window.location.origin },
      })
    },
    signOut: async () => { await supabase.auth.signOut(); setMe(null) },
  }
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export const useAuth = () => useContext(Ctx)
