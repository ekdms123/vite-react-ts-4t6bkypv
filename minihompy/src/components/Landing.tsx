import { useState } from 'react'
import { useAuth } from '../lib/auth'

/**
 * 로그인 전 화면. 이메일·비밀번호가 기본이고 구글은 곁다리로 둔다.
 * 구글은 Supabase에서 켜야 작동하므로, 안 켜져 있으면 안내로 바뀐다.
 */
export default function Landing() {
  const { signInEmail, signUpEmail, signInGoogle } = useAuth()
  const [mode, setMode] = useState<'in' | 'up'>('in')
  const [email, setEmail] = useState('')
  const [pw, setPw] = useState('')
  const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)

  async function go() {
    if (!email.trim() || pw.length < 6) {
      setMsg(pw.length < 6 ? '비밀번호는 6글자 이상.' : '이메일을 적어야 한다.')
      return
    }
    setBusy(true); setMsg('')
    try {
      const err = mode === 'in'
        ? await signInEmail(email.trim(), pw)
        : await signUpEmail(email.trim(), pw)
      if (err) setMsg(err)
      else if (mode === 'up') setMsg('가입됐다. 바로 못 들어가면 메일함의 인증 링크를 눌러야 한다.')
    } finally { setBusy(false) }
  }

  async function google() {
    setMsg('')
    try { await signInGoogle() }
    catch { setMsg('구글 로그인이 아직 안 켜져 있다. 이메일로 들어가면 된다.') }
  }

  return (
    <div className="stage">
      <div className="binder-wrap" style={{ maxWidth: 400, paddingRight: 0 }}>
        <div className="binder">
          <div className="gate">
            <div className="home-name" style={{ fontSize: 17 }}>미니홈피</div>
            <p className="k soft" style={{ lineHeight: 1.9, padding: '10px 0 18px' }}>
              오늘 할 일, 달력, 일기, 가계부, 챌린지.<br />
              한 집에 다 있고, 방명록도 있다.
            </p>

            <div className="gate-tabs">
              <button data-on={mode === 'in'} onClick={() => { setMode('in'); setMsg('') }}>
                로그인
              </button>
              <button data-on={mode === 'up'} onClick={() => { setMode('up'); setMsg('') }}>
                처음이에요
              </button>
            </div>

            <input type="email" placeholder="이메일" value={email} autoComplete="email"
                   onChange={e => setEmail(e.target.value)} />
            <input type="password" placeholder="비밀번호 (6글자 이상)" value={pw}
                   autoComplete={mode === 'in' ? 'current-password' : 'new-password'}
                   onChange={e => setPw(e.target.value)}
                   onKeyDown={e => { if (e.key === 'Enter') void go() }} />

            {msg && <div className="gate-msg">{msg}</div>}

            <button className="btn gate-go" onClick={go} disabled={busy}>
              {busy ? '…' : mode === 'in' ? '들어가기' : '내 집 만들기'}
            </button>

            <div className="gate-or"><span>또는</span></div>
            <button className="btn ghost" style={{ width: '100%' }} onClick={google}>
              구글로 계속하기
            </button>

            <p className="k soft" style={{ paddingTop: 14, fontSize: 10, lineHeight: 1.7 }}>
              들어가면 내 집이 하나 생긴다.<br />
              친구도 여기서 가입하면 서로 일촌을 맺을 수 있다.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
