import { useCallback, useEffect, useState } from 'react'
import { isConfigured } from './lib/supabase'
import { useAuth } from './lib/auth'
import * as api from './lib/api'
import { useIsDesktop } from './lib/useIsDesktop'
import type { EnergyKey, Profile, Section } from './lib/types'
import LeftPage from './components/LeftPage'
import TabRail from './components/TabRail'
import HomePanel from './components/HomePanel'
import Friends from './components/Friends'
import Settings from './components/Settings'
import Search from './components/Search'
import SectionView from './sections/SectionView'
import { warmSections } from './sections/lazy'
import Landing from './components/Landing'
import Setup from './components/Setup'

/** #/@handle · #/friends · #/settings — 해시 하나로 충분하다. */
function useHashRoute() {
  const [hash, setHash] = useState(() => location.hash || '#/')
  useEffect(() => {
    const on = () => setHash(location.hash || '#/')
    addEventListener('hashchange', on)
    return () => removeEventListener('hashchange', on)
  }, [])
  return hash
}

export default function App() {
  const { session, me, loading, refreshMe, signOut } = useAuth()
  const hash = useHashRoute()
  const isDesktop = useIsDesktop()

  const [viewing, setViewing] = useState<Profile | null>(null)
  const [sections, setSections] = useState<Section[]>([])
  const [tab, setTab] = useState('home')
  const [visits, setVisits] = useState({ today: 0, total: 0 })
  const [energy, setEnergy] = useState<EnergyKey>(
    () => (localStorage.getItem('energy') as EnergyKey) || 'mid')
  const [notFound, setNotFound] = useState(false)
  const [stat, setStat] = useState<Awaited<ReturnType<typeof api.roomStat>> | null>(null)

  const wantedHandle = hash.startsWith('#/@') ? hash.slice(3).split('/')[0] : null
  const sheet = hash === '#/friends' ? 'friends'
              : hash === '#/settings' ? 'settings'
              : hash === '#/find' ? 'find' : null

  /** 볼 집을 정한다. 주소가 있으면 그 집, 없으면 내 집. */
  const load = useCallback(async () => {
    const target = wantedHandle
      ? await api.getProfileByHandle(wantedHandle)
      : me
    if (wantedHandle && !target) { setNotFound(true); setViewing(null); return }
    setNotFound(false)
    setViewing(target ?? null)
    if (!target) { setSections([]); return }
    setSections(await api.listSections(target.id))
    setVisits(await api.getVisitCounts(target.id))
    setStat(await api.roomStat(target.id))
  }, [wantedHandle, me])

  useEffect(() => { void load() }, [load])

  // 남의 집에 들어가면 카운터를 올린다. 내 집은 안 올린다.
  useEffect(() => {
    if (!viewing || !me || viewing.id === me.id) return
    const seen = sessionStorage.getItem('v:' + viewing.id)
    if (seen) return
    sessionStorage.setItem('v:' + viewing.id, '1')
    void api.bumpVisit(viewing.id).then(() => api.getVisitCounts(viewing.id)).then(setVisits)
  }, [viewing, me])

  useEffect(() => { setTab('home') }, [viewing?.id])
  useEffect(() => { if (me) warmSections() }, [me])
  useEffect(() => { localStorage.setItem('energy', energy) }, [energy])
  useEffect(() => {
    document.documentElement.dataset.skin = viewing?.skin_key ?? 'sky'
  }, [viewing?.skin_key])

  async function wave() {
    // 파도타기: 일촌 중에 아무 집이나. 없으면 내 집에 머문다.
    if (!me) return
    const fs = (await api.listFriendships(me.id)).filter(f => f.status === 'accepted')
    if (!fs.length) { alert('아직 일촌이 없다.'); return }
    const f = fs[Math.floor(Math.random() * fs.length)]
    const otherId = f.requester === me.id ? f.addressee : f.requester
    const p = await api.getProfileById(otherId)
    if (p) location.hash = `#/@${p.handle}`
  }

  if (!isConfigured) return <NeedsKeys />
  if (loading) return <div className="stage"><div className="boot">여는 중…</div></div>
  if (!session) return <Landing />
  if (!me) return <div className="stage"><div className="boot">집을 짓는 중…</div></div>
  if (notFound) return (
    <div className="stage"><div className="boot">
      그런 주소는 없다.<br />
      <a href="#/">내 집으로</a>
    </div></div>
  )
  if (!viewing) return <div className="stage"><div className="boot">불러오는 중…</div></div>

  const isOwner = viewing.id === me.id
  const current = sections.find(s => s.id === tab)

  return (
    <div className="stage">
      <div className="binder-wrap">
        <div className="binder">
          <div className="spread">
            <aside aria-label="프로필"><LeftPage profile={viewing} isOwner={isOwner} visits={visits} stat={stat}
                      energy={energy} onEnergy={setEnergy}
                      onChanged={() => { void refreshMe(); void load() }}
                      onWave={wave} /></aside>

            {isDesktop && (
              <div className="rings" aria-hidden>
                {Array.from({ length: 4 }, (_, i) => <span key={i} className="ring" />)}
              </div>
            )}

            <main className="page-right">
              <div className="right-head">
                <h1>{viewing.title}</h1>
                <span className="sr-only" aria-hidden="false">{viewing.title}</span>
                <div className="acts">
                  {!isOwner && <button onClick={() => location.hash = '#/friends'}>+일촌맺기</button>}
                  {isOwner && <button onClick={() => location.hash = '#/find'}>찾기</button>}
                  {isOwner && <button onClick={() => location.hash = '#/settings'}>꾸미기</button>}
                  <button onClick={signOut}>로그아웃</button>
                </div>
                <span className="url">/#/@{viewing.handle}</span>
              </div>

              <div className="right-body">
                {tab === 'home'
                  ? <HomePanel profile={viewing} sections={sections} isOwner={isOwner}
                               uid={me.id} energy={energy} onJump={setTab} />
                  : current
                    ? <SectionView section={current} sections={sections} owner={viewing}
                                 isOwner={isOwner} uid={me.id} />
                    : <div className="empty-note">없는 탭이다.</div>}
              </div>
            </main>
          </div>

          <TabRail sections={sections} current={tab} onPick={setTab}
                   isOwner={isOwner} onAdd={() => location.hash = '#/settings'} />
        </div>
      </div>

      {!isDesktop && (
        <div className="dock">
          <button className="btn" onClick={() => setTab('home')}>홈</button>
          {isOwner && <button className="btn ghost"
                              onClick={() => location.hash = '#/find'}>찾기</button>}
          <button className="btn ghost" onClick={() => location.hash = '#/friends'}>일촌</button>
          {isOwner && <button className="btn ghost"
                              onClick={() => location.hash = '#/settings'}>꾸미기</button>}
        </div>
      )}

      {sheet === 'find' && isOwner &&
        <Search me={me} onJump={setTab} onClose={() => (location.hash = '#/')} />}
      {sheet === 'friends'  && <Friends me={me} onClose={() => (location.hash = '#/')} />}
      {sheet === 'settings' && isOwner &&
        <Settings me={me} sections={sections}
                  onChanged={() => { void refreshMe(); void load() }}
                  onClose={() => (location.hash = '#/')} />}

      {me && me.handle.startsWith('u') && me.handle.length === 9 && !sheet && (
        <Setup me={me} onDone={() => { void refreshMe(); void load() }} />
      )}
    </div>
  )
}

function NeedsKeys() {
  return (
    <div className="stage"><div className="boot needs-keys">
      <b>연결이 아직 안 됐다.</b>
      <p>
        <code>minihompy/.env</code> 파일을 만들고 Supabase 키 두 줄을 넣어야 한다.
        <code>.env.example</code>에 모양이 있다.
      </p>
    </div></div>
  )
}
