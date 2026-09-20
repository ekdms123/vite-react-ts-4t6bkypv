import { useEffect, useState } from 'react'
import * as api from '../lib/api'
import { DECOR_BG, FRAMES, type Comment, type Decor, type Entry } from '../lib/types'

/**
 * 사진 한 장이 곧 한 페이지다. 배경과 테두리와 아래 적는 글귀를 사진마다
 * 따로 갖고, 그 아래에 댓글이 붙는다. 싸이월드 사진첩이 오래 살아 있던
 * 이유는 사진이 아니라 그 아래였다.
 */
export default function PhotoPage({ entry, isOwner, uid, onBack }: {
  entry: Entry; isOwner: boolean; uid: string | null; onBack: () => void
}) {
  const [decor, setDecor] = useState<Decor>((entry.decor ?? {}) as Decor)
  const [title, setTitle] = useState(entry.title)
  const [rows, setRows] = useState<Comment[]>([])
  const [body, setBody] = useState('')
  const [editing, setEditing] = useState(false)
  const [busy, setBusy] = useState(false)

  async function reload() { setRows(await api.listComments(entry.id)) }
  useEffect(() => { void reload() /* eslint-disable-next-line */ }, [entry.id])

  async function save(next: Decor, nextTitle = title) {
    setDecor(next); setTitle(nextTitle)
    await api.updateEntry(entry.id, { decor: next, title: nextTitle })
  }

  async function send() {
    if (!uid || !body.trim()) return
    setBusy(true)
    try { await api.addComment(entry.id, uid, body.trim()); setBody(''); await reload() }
    finally { setBusy(false) }
  }

  const frame = decor.frame ?? 'polaroid'
  const dark = decor.bg === '#2b2b30'

  return (
    <div className="photopage" style={{ background: decor.bg ?? '#fff' }} data-dark={dark}>
      <div className="pp-bar">
        <button className="crumb" onClick={onBack}>‹ 앨범으로</button>
        {isOwner && (
          <button className="crumb" onClick={() => setEditing(v => !v)}>
            {editing ? 'done' : '꾸미기'}
          </button>
        )}
      </div>

      {editing && isOwner && (
        <div className="pp-tools">
          <div className="pp-row">
            <span>배경</span>
            {DECOR_BG.map(c => (
              <button key={c} className="swatch" style={{ background: c }}
                      data-on={(decor.bg ?? '#ffffff') === c}
                      onClick={() => save({ ...decor, bg: c })} aria-label={c} />
            ))}
          </div>
          <div className="pp-row">
            <span>테두리</span>
            {FRAMES.map(f => (
              <button key={f.key} className="pill" data-on={frame === f.key}
                      onClick={() => save({ ...decor, frame: f.key })}>{f.label}</button>
            ))}
          </div>
          <input type="text" placeholder="사진 제목" value={title}
                 onChange={e => setTitle(e.target.value)}
                 onBlur={() => save(decor, title)} />
          <textarea rows={3} placeholder="이 사진에 대해 적어두기"
                    value={decor.note ?? ''}
                    onChange={e => setDecor({ ...decor, note: e.target.value })}
                    onBlur={() => save(decor)} />
        </div>
      )}

      <figure className={`pp-photo frame-${frame}`}>
        <img src={entry.images[0]} alt={title || ''} />
        {title && <figcaption>{title}</figcaption>}
      </figure>

      {decor.note && <p className="pp-note">{decor.note}</p>}

      <div className="pp-comments">
        <div className="news-title">댓글 {rows.length}</div>
        {rows.length === 0 && <div className="empty-note">아직 댓글이 없다.</div>}
        {rows.map(c => (
          <div key={c.id} className="pp-c">
            <div className="ava">
              {c.author_profile?.avatar_url && <img src={c.author_profile.avatar_url} alt="" />}
            </div>
            <div className="pp-c-body">
              <b>{c.author_profile?.title ?? '누군가'}</b>
              <span className="when">
                {new Date(c.created_at).toLocaleDateString('ko-KR',
                  { month: 'numeric', day: 'numeric' })}
              </span>
              <p>{c.body}</p>
            </div>
            {(uid === c.author || isOwner) && (
              <button className="x" aria-label="지우기" onClick={async () => {
                await api.deleteComment(c.id); await reload()
              }}>×</button>
            )}
          </div>
        ))}

        {uid && (
          <div className="quick-add" style={{ marginTop: 10 }}>
            <input type="text" placeholder="한마디" value={body}
                   onChange={e => setBody(e.target.value)}
                   onKeyDown={e => { if (e.key === 'Enter') void send() }} />
            <button className="btn" onClick={send} disabled={busy || !body.trim()}>달기</button>
          </div>
        )}
      </div>
    </div>
  )
}
