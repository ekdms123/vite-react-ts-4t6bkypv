import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import { MOODS, type Entry, type Section } from '../lib/types'
import Editable from '../components/Editable'

const MOOD_FACE: Record<string, string> = {
  행복: '🌷', 뿌듯: '🌟', 설렘: '🎀', 그냥그럼: '☁️', 피곤: '🫧',
  심란: '🌀', 우울: '🌧', 신남: '🎈', 멍함: '🌙',
}
const WEATHER = ['', '☀️', '⛅', '🌧', '❄️', '🌬']

/** 날짜를 찢어낸 달력 쪽지로 세우고, 그 옆에 그날 하루를 붙인다. */
export default function Diary({ section, isOwner, uid }: {
  section: Section; isOwner: boolean; uid: string | null
}) {
  const [rows, setRows] = useState<Entry[]>([])
  const [open, setOpen] = useState(false)
  const [body, setBody] = useState('')
  const [mood, setMood] = useState('')
  const [weather, setWeather] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [busy, setBusy] = useState(false)

  async function reload() { setRows(await api.listEntries(section.id)) }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [section.id])

  async function save() {
    if (!uid || !body.trim()) return
    setBusy(true)
    try {
      const images: string[] = []
      for (const f of files) images.push(await api.uploadImage(uid, f, 'diary'))
      await api.createEntry({
        section_id: section.id, owner: uid,
        title: body.trim().split('\n')[0].slice(0, 40),
        body: body.trim(), mood, weather, images,
        visibility: section.visibility,
      })
      setBody(''); setMood(''); setWeather(''); setFiles([]); setOpen(false)
      await reload()
    } finally { setBusy(false) }
  }

  return (
    <div>
      <div className="sec-title">
        {section.label}
        <span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>{rows.length}일</span>
      </div>

      {isOwner && (open ? (
        <div className="diary-write">
          <div className="dw-row">
            <select value={mood} onChange={e => setMood(e.target.value)}>
              {MOODS.map(m => <option key={m} value={m}>{m ? `${MOOD_FACE[m] ?? ''} ${m}` : '오늘 기분'}</option>)}
            </select>
            <div className="weather-pick">
              {WEATHER.slice(1).map(w => (
                <button key={w} data-on={weather === w}
                        onClick={() => setWeather(weather === w ? '' : w)}>{w}</button>
              ))}
            </div>
          </div>
          <textarea rows={6} autoFocus placeholder="오늘 뭐 했더라…  한 줄이어도 된다."
                    value={body} onChange={e => setBody(e.target.value)} />
          <div className="dw-row">
            <input type="file" accept="image/*" multiple
                   onChange={e => setFiles(Array.from(e.target.files ?? []))} />
            <button className="btn ghost" onClick={() => setOpen(false)}>접기</button>
            <button className="btn" onClick={save} disabled={busy || !body.trim()}>
              {busy ? '…' : '붙이기'}
            </button>
          </div>
        </div>
      ) : (
        <button className="diary-open" onClick={() => setOpen(true)}>
          ✎ 오늘 쓰기
        </button>
      ))}

      {rows.length === 0
        ? <div className="empty-note">아직 쓴 날이 없다.<br />한 줄이면 된다.</div>
        : <div className="diary-list">
            {rows.map(r => {
              const d = new Date(r.created_at)
              return (
                <article key={r.id} className="diary-day">
                  <div className="tearoff">
                    <b>{d.getDate()}</b>
                    <span>{d.getMonth() + 1}월</span>
                    <em>{['일','월','화','수','목','금','토'][d.getDay()]}</em>
                  </div>
                  <div className="diary-body">
                    <div className="diary-meta">
                      {r.mood && <span className="mood-tag">{MOOD_FACE[r.mood] ?? ''} {r.mood}</span>}
                      {r.weather && <span className="wx">{r.weather}</span>}
                      {isOwner && (
                        <button className="x" style={{ marginLeft: 'auto' }}
                                onClick={async () => {
                                  if (confirm('지울까?')) { await api.deleteEntry(r.id); await reload() }
                                }}>×</button>
                      )}
                    </div>
                    <Editable className="diary-text" value={r.body} multiline
                              disabled={!isOwner} placeholder="비어 있다"
                              onSave={async next => {
                                await api.updateEntry(r.id, { body: next }); await reload()
                              }} />
                    {r.images.length > 0 && (
                      <div className="diary-pics">
                        {r.images.map((src, i) => <img key={i} src={src} alt="" loading="lazy" />)}
                      </div>
                    )}
                  </div>
                </article>
              )
            })}
          </div>}
    </div>
  )
}
