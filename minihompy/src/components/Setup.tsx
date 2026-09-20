import { useState } from 'react'
import * as api from '../lib/api'
import type { Profile } from '../lib/types'

/** 가입 직후 한 번. 주소와 이름만 받고 끝낸다. */
export default function Setup({ me, onDone }: { me: Profile; onDone: () => void }) {
  const [handle, setHandle] = useState('')
  const [title, setTitle] = useState(me.title)
  const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)

  async function save() {
    const h = api.normalizeHandle(handle)
    if (h.length < 2) { setMsg('영문·숫자·밑줄로 2글자 이상.'); return }
    setBusy(true)
    try {
      if (!(await api.isHandleFree(h, me.id))) { setMsg('이미 쓰는 주소다.'); return }
      await api.updateProfile(me.id, { handle: h, title: title.trim() || `${h}의 미니홈피` })
      onDone()
    } finally { setBusy(false) }
  }

  return (
    <div className="sheet">
      <div className="sheet-head"><b>집 주소 정하기</b></div>
      <section className="block">
        <p className="k soft" style={{ lineHeight: 1.8, paddingBottom: 10 }}>
          친구한테 보낼 주소다. 나중에 바꿔도 된다.
        </p>
        <label className="field">
          <span>주소</span>
          <div className="addr">
            <em>/#/@</em>
            <input type="text" value={handle} autoFocus placeholder="daeun"
                   onChange={e => setHandle(e.target.value)}
                   onKeyDown={e => { if (e.key === 'Enter') void save() }} />
          </div>
        </label>
        <label className="field">
          <span>이름</span>
          <input type="text" value={title} onChange={e => setTitle(e.target.value)} />
        </label>
        {msg && <div className="k soft" style={{ color: '#c0392b' }}>{msg}</div>}
        <button className="btn" onClick={save} disabled={busy || !handle.trim()}>
          이 주소로 시작
        </button>
      </section>
    </div>
  )
}
