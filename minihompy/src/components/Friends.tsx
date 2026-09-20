import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import type { Friendship, Profile } from '../lib/types'

/** 일촌. 한쪽이 신청하고 다른 쪽이 받아야 맺어진다. */
export default function Friends({ me, onClose }: { me: Profile; onClose: () => void }) {
  const [rows, setRows] = useState<Friendship[]>([])
  const [people, setPeople] = useState<Record<string, Profile>>({})
  const [handle, setHandle] = useState('')
  const [note, setNote] = useState('')
  const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)

  async function reload() {
    const fs = await api.listFriendships(me.id)
    setRows(fs)
    const ids = [...new Set(fs.flatMap(f => [f.requester, f.addressee]))]
      .filter(id => id !== me.id)
    const ps = await api.profilesByIds(ids)
    setPeople(Object.fromEntries(ps.map(p => [p.id, p])))
  }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [me.id])

  async function send() {
    setBusy(true); setMsg('')
    try {
      const target = await api.getProfileByHandle(api.normalizeHandle(handle))
      if (!target)            { setMsg('그런 주소는 없다.'); return }
      if (target.id === me.id) { setMsg('자기 자신에게는 못 건다.'); return }
      await api.requestFriend(me.id, target.id, note.trim())
      setHandle(''); setNote(''); setMsg('신청했다. 상대가 받으면 맺어진다.')
      await reload()
    } catch (e) {
      setMsg(e instanceof Error && e.message.includes('duplicate')
        ? '이미 신청했다.' : '신청에 실패했다.')
    } finally { setBusy(false) }
  }

  const incoming = rows.filter(f => f.status === 'pending' && f.addressee === me.id)
  const outgoing = rows.filter(f => f.status === 'pending' && f.requester === me.id)
  const friends  = rows.filter(f => f.status === 'accepted')

  const other = (f: Friendship) => people[f.requester === me.id ? f.addressee : f.requester]

  return (
    <div className="sheet">
      <div className="sheet-head">
        <b>일촌</b>
        <button className="btn ghost" onClick={onClose}>닫기</button>
      </div>

      <section className="block">
        <div className="news-title">일촌 신청</div>
        <div className="quick-add">
          <input type="text" placeholder="상대 주소 (예: daeun)" value={handle}
                 onChange={e => setHandle(e.target.value)} style={{ width: 150 }} />
          <input type="text" placeholder="일촌평 한 줄" value={note}
                 onChange={e => setNote(e.target.value)} />
          <button className="btn" onClick={send} disabled={busy || !handle.trim()}>신청</button>
        </div>
        {msg && <div className="k soft">{msg}</div>}
      </section>

      {incoming.length > 0 && (
        <section className="block">
          <div className="news-title">받은 신청 {incoming.length}</div>
          {incoming.map(f => (
            <div key={f.id} className="friend-row">
              <b>{other(f)?.title ?? '누군가'}</b>
              <span className="k">{f.requester_note}</span>
              <button className="btn" onClick={async () => {
                await api.acceptFriend(f.id, ''); await reload()
              }}>받기</button>
              <button className="btn ghost" onClick={async () => {
                await api.removeFriend(f.id); await reload()
              }}>거절</button>
            </div>
          ))}
        </section>
      )}

      <section className="block">
        <div className="news-title">내 일촌 {friends.length}</div>
        {friends.length === 0
          ? <div className="empty-note">아직 일촌이 없다.</div>
          : friends.map(f => {
              const p = other(f)
              return (
                <div key={f.id} className="friend-row">
                  <div className="ava">{p?.avatar_url && <img src={p.avatar_url} alt="" />}</div>
                  <b>{p?.title ?? '누군가'}</b>
                  <span className="k">
                    {f.requester === me.id ? f.addressee_note : f.requester_note}
                  </span>
                  <a href={`#/@${p?.handle}`} onClick={onClose}>놀러가기</a>
                  <button className="btn ghost" onClick={async () => {
                    if (confirm('끊을까?')) { await api.removeFriend(f.id); await reload() }
                  }}>끊기</button>
                </div>
              )
            })}
      </section>

      {outgoing.length > 0 && (
        <section className="block">
          <div className="news-title">보낸 신청 {outgoing.length}</div>
          {outgoing.map(f => (
            <div key={f.id} className="friend-row">
              <b>{other(f)?.title ?? '…'}</b>
              <span className="k">기다리는 중</span>
              <button className="btn ghost" onClick={async () => {
                await api.removeFriend(f.id); await reload()
              }}>취소</button>
            </div>
          ))}
        </section>
      )}
    </div>
  )
}
