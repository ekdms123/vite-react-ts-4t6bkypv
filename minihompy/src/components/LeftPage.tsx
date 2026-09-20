import { useRef } from 'react'
import * as api from '../lib/api'
import { ENERGY, MOODS, type EnergyKey, type Profile } from '../lib/types'

interface Props {
  profile: Profile
  isOwner: boolean
  visits: { today: number; total: number }
  energy: EnergyKey
  onEnergy: (e: EnergyKey) => void
  onChanged: () => void
  onWave: () => void
}

/** 바인더 왼쪽 면. 카운터 · 기분 · 미니미 · 이름 · 파도타기. */
export default function LeftPage({
  profile, isOwner, visits, energy, onEnergy, onChanged, onWave,
}: Props) {
  const fileRef = useRef<HTMLInputElement>(null)

  async function pickAvatar(file: File) {
    const url = await api.uploadImage(profile.id, file, 'avatar')
    await api.updateProfile(profile.id, { avatar_url: url })
    onChanged()
  }

  return (
    <div className="page-left">
      <div className="counter">
        TODAY <b>{visits.today}</b> | TOTAL <span className="total">{profile.total_visits}</span>
      </div>

      <div className="left-card">
        <div className="minimi">
          {profile.avatar_url
            ? <img src={profile.avatar_url} alt="프사" />
            : <span className="empty">프사<br />없음</span>}
          {isOwner && (
            <>
              <button className="upload" onClick={() => fileRef.current?.click()}>사진 바꾸기</button>
              <input ref={fileRef} type="file" accept="image/*" hidden
                     onChange={e => { const f = e.target.files?.[0]; if (f) void pickAvatar(f) }} />
            </>
          )}
        </div>

        <div className="left-head-text">
          <div className="home-name">{profile.title}</div>
          {profile.tagline && <div className="home-tagline">{profile.tagline}</div>}

          <div className="mood-row">
            <span className="label">TODAY IS..</span>
            <select value={profile.mood} disabled={!isOwner} aria-label="오늘 기분"
                    onChange={async e => {
                      await api.updateProfile(profile.id, { mood: e.target.value }); onChanged()
                    }}>
              {MOODS.map(m => <option key={m} value={m}>{m || '—'}</option>)}
            </select>
          </div>

          {isOwner && (
            <div className="energy">
              {ENERGY.map(e => (
                <button key={e.key} data-on={energy === e.key} onClick={() => onEnergy(e.key)}>
                  {e.label}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="left-links">
          {isOwner && <button onClick={() => location.hash = '#/settings'}>EDIT</button>}
          <button onClick={() => location.hash = '#/friends'}>일촌</button>
        </div>

        <div className="wave">
          <span>파도타기</span>
          <button onClick={onWave} aria-label="파도타기 — 일촌 집에 가기">▲</button>
        </div>
      </div>
    </div>
  )
}
