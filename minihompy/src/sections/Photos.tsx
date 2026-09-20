import { useEffect, useRef, useState } from 'react'
import * as api from '../lib/api'
import type { Entry, Section } from '../lib/types'

/** 폴라로이드. 아래 흰 여백에 한 줄 적는 자리가 있다. */
export default function Photos({ section, isOwner, uid }: {
  section: Section; isOwner: boolean; uid: string | null
}) {
  const [rows, setRows] = useState<Entry[]>([])
  const [zoom, setZoom] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  async function reload() { setRows(await api.listEntries(section.id)) }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [section.id])

  async function upload(files: FileList) {
    if (!uid || !files.length) return
    setBusy(true)
    try {
      for (const f of Array.from(files)) {
        const url = await api.uploadImage(uid, f, 'photo')
        await api.createEntry({
          section_id: section.id, owner: uid, title: '', images: [url],
          visibility: section.visibility,
        })
      }
      await reload()
    } finally { setBusy(false) }
  }

  const shots = rows.flatMap(r => r.images.map(src => ({ id: r.id, src, cap: r.title })))

  return (
    <div>
      <div className="sec-title">
        {section.label}
        <span style={{ float: 'right', fontWeight: 400, color: '#b0b0b0' }}>{shots.length}장</span>
      </div>

      {isOwner && (
        <>
          <button className="photo-drop" onClick={() => fileRef.current?.click()} disabled={busy}>
            {busy ? '올리는 중…' : '＋ 사진 올리기'}
          </button>
          <input ref={fileRef} type="file" accept="image/*" multiple hidden
                 onChange={e => e.target.files && upload(e.target.files)} />
        </>
      )}

      {shots.length === 0
        ? <div className="empty-note">사진이 없다.</div>
        : <div className="polaroids">
            {shots.map((s, i) => (
              <figure key={`${s.id}-${i}`} style={{ '--tilt': `${(i % 5) - 2}deg` } as React.CSSProperties}>
                <img src={s.src} alt={s.cap || ''} loading="lazy" onClick={() => setZoom(s.src)} />
                <figcaption>
                  {isOwner ? (
                    <input type="text" defaultValue={s.cap} placeholder="한 줄"
                           onBlur={async e => {
                             if (e.target.value !== s.cap) {
                               await api.updateEntry(s.id, { title: e.target.value }); await reload()
                             }
                           }} />
                  ) : <span>{s.cap}</span>}
                </figcaption>
                {isOwner && (
                  <button className="pull" title="빼기"
                          onClick={async () => {
                            if (confirm('뺄까?')) { await api.deleteEntry(s.id); await reload() }
                          }}>×</button>
                )}
              </figure>
            ))}
          </div>}

      {zoom && (
        <div className="lightbox" onClick={() => setZoom(null)}>
          <img src={zoom} alt="" />
        </div>
      )}
    </div>
  )
}
