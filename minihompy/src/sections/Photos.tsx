import { useEffect, useRef, useState } from 'react'
import * as api from '../lib/api'
import type { Entry, Section } from '../lib/types'
import PhotoPage from './PhotoPage'

type Album = Awaited<ReturnType<typeof api.listAlbums>>[number]

/** 앨범 → 사진 → 한 장짜리 페이지. 세 겹으로 들어간다. */
export default function Photos({ section, isOwner, uid }: {
  section: Section; isOwner: boolean; uid: string | null
}) {
  const [albums, setAlbums] = useState<Album[]>([])
  const [album, setAlbum] = useState<string | null>(null)
  const [shots, setShots] = useState<Entry[]>([])
  const [counts, setCounts] = useState<Record<string, number>>({})
  const [open, setOpen] = useState<Entry | null>(null)
  const [busy, setBusy] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  async function reloadAlbums() { setAlbums(await api.listAlbums(section.id)) }
  async function reloadShots(name: string) {
    const rows = await api.listInAlbum(section.id, name)
    setShots(rows)
    setCounts(await api.commentCounts(rows.map(r => r.id)))
  }

  useEffect(() => { void reloadAlbums(); setAlbum(null)
    /* eslint-disable-next-line */ }, [section.id])
  useEffect(() => { if (album) void reloadShots(album)
    /* eslint-disable-next-line */ }, [album])

  async function upload(files: FileList) {
    if (!uid || !files.length) return
    setBusy(true)
    try {
      for (const f of Array.from(files)) {
        const url = await api.uploadImage(uid, f, 'photo')
        await api.createEntry({
          section_id: section.id, owner: uid, title: '', images: [url],
          category: album ?? '기본', visibility: section.visibility,
        })
      }
      await reloadAlbums()
      if (album) await reloadShots(album)
    } finally { setBusy(false) }
  }

  async function newAlbum() {
    const name = prompt('앨범 이름')?.trim()
    if (!name) return
    setAlbum(name)   // 첫 사진이 올라가면 그때 앨범이 생긴다
    setShots([])
  }

  if (open) {
    return (
      <PhotoPage entry={open} isOwner={isOwner} uid={uid}
                 onBack={() => { setOpen(null); if (album) void reloadShots(album) }} />
    )
  }

  // ── 앨범 목록 ──
  if (!album) {
    return (
      <div>
        <div className="sec-title">
          {section.label}
          <span style={{ float: 'right', fontWeight: 400, color: '#636363' }}>
            앨범 {albums.length}
          </span>
        </div>
        {isOwner && (
          <button className="photo-drop" onClick={newAlbum}>＋ 새 앨범</button>
        )}
        {albums.length === 0
          ? <div className="empty-note">아직 앨범이 없다.</div>
          : <div className="albums">
              {albums.map(a => (
                <button key={a.name} className="album" onClick={() => setAlbum(a.name)}>
                  <div className="album-cover">
                    {a.cover ? <img src={a.cover} alt="" loading="lazy" /> : <span>비어 있음</span>}
                    <i className="album-back" />
                  </div>
                  <div className="album-name">{a.name}</div>
                  <div className="album-count">{a.count}장</div>
                </button>
              ))}
            </div>}
      </div>
    )
  }

  // ── 앨범 안 ──
  return (
    <div>
      <div className="sec-title crumbs">
        <button className="crumb" onClick={() => { setAlbum(null); void reloadAlbums() }}>
          ‹ 앨범
        </button>
        <span>{album}</span>
        {isOwner && (
          <button className="crumb rename" onClick={async () => {
            const to = prompt('앨범 이름 바꾸기', album)?.trim()
            if (to && to !== album) {
              await api.renameAlbum(section.id, album, to)
              await reloadAlbums(); setAlbum(to)
            }
          }}>이름</button>
        )}
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
        ? <div className="empty-note">이 앨범은 비어 있다.</div>
        : <div className="polaroids">
            {shots.map((s, i) => (
              <figure key={s.id} style={{ '--tilt': `${(i % 5) - 2}deg` } as React.CSSProperties}>
                <img src={s.images[0]} alt={s.title || ''} loading="lazy"
                     onClick={() => setOpen(s)} />
                <figcaption>
                  <span>{s.title || ' '}</span>
                  {counts[s.id] ? <em className="cbadge">💬 {counts[s.id]}</em> : null}
                </figcaption>
              </figure>
            ))}
          </div>}
    </div>
  )
}
