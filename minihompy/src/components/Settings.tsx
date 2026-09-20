import { useState } from 'react'
import * as api from '../lib/api'
import { todayKey } from '../lib/day'
import { CREATABLE_KINDS, KIND_LABEL, SKINS, type Profile, type Section, type SectionKind } from '../lib/types'

/** 주소 · 이름 · 스킨 · 탭 구성 · 백업. 전부 본인만 만진다. */
export default function Settings({ me, sections, onChanged, onClose }: {
  me: Profile; sections: Section[]; onChanged: () => void; onClose: () => void
}) {
  const [handle, setHandle] = useState(me.handle)
  const [title, setTitle] = useState(me.title)
  const [tagline, setTagline] = useState(me.tagline)
  const [msg, setMsg] = useState('')
  const [newLabel, setNewLabel] = useState('')
  const [newKind, setNewKind] = useState<SectionKind>('free')

  async function saveProfile() {
    const h = api.normalizeHandle(handle)
    if (h.length < 2) { setMsg('주소는 2글자 이상, 영문·숫자·밑줄만.'); return }
    if (!(await api.isHandleFree(h, me.id))) { setMsg('이미 쓰는 주소다.'); return }
    await api.updateProfile(me.id, { handle: h, title, tagline })
    setHandle(h); setMsg('저장했다.'); onChanged()
  }

  async function addSection() {
    if (!newLabel.trim()) return
    await api.createSection(me.id, newLabel.trim(), newKind, sections.length + 1)
    setNewLabel(''); onChanged()
  }

  async function move(s: Section, dir: -1 | 1) {
    const i = sections.findIndex(x => x.id === s.id)
    const j = i + dir
    if (j < 0 || j >= sections.length) return
    await Promise.all([
      api.updateSection(s.id, { position: sections[j].position }),
      api.updateSection(sections[j].id, { position: s.position }),
    ])
    onChanged()
  }

  return (
    <div className="sheet">
      <div className="sheet-head">
        <b>꾸미기 · 설정</b>
        <button className="btn ghost" onClick={onClose}>닫기</button>
      </div>

      <section className="block">
        <div className="news-title">내 미니홈피</div>
        <label className="field">
          <span>주소</span>
          <div className="addr">
            <em>{location.origin}/#/@</em>
            <input type="text" value={handle} onChange={e => setHandle(e.target.value)} />
          </div>
        </label>
        <label className="field">
          <span>이름</span>
          <input type="text" value={title} onChange={e => setTitle(e.target.value)} />
        </label>
        <label className="field">
          <span>한 줄</span>
          <textarea rows={2} value={tagline} onChange={e => setTagline(e.target.value)} />
        </label>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button className="btn" onClick={saveProfile}>저장</button>
          {msg && <span className="k soft">{msg}</span>}
        </div>
      </section>

      <section className="block">
        <div className="news-title">스킨</div>
        <div className="skins">
          {SKINS.map(s => (
            <button key={s.key} data-on={me.skin_key === s.key} data-skin={s.key}
                    onClick={async () => {
                      await api.updateProfile(me.id, { skin_key: s.key }); onChanged()
                    }}>
              {s.label}
            </button>
          ))}
        </div>
      </section>

      <section className="block">
        <div className="news-title">탭</div>
        {sections.map(s => (
          <div key={s.id} className="tab-row">
            <input type="text" defaultValue={s.label}
                   onBlur={async e => {
                     if (e.target.value.trim() && e.target.value !== s.label) {
                       await api.updateSection(s.id, { label: e.target.value.trim() }); onChanged()
                     }
                   }} />
            <span className="chip">{KIND_LABEL[s.kind]}</span>
            <select value={s.visibility}
                    onChange={async e => {
                      await api.updateSection(s.id, { visibility: e.target.value as Section['visibility'] })
                      onChanged()
                    }}>
              <option value="public">전체공개</option>
              <option value="friends">일촌만</option>
              <option value="private">나만</option>
            </select>
            <button className="btn ghost" onClick={() => move(s, -1)}>↑</button>
            <button className="btn ghost" onClick={() => move(s, 1)}>↓</button>
            <button className="btn ghost" onClick={async () => {
              if (confirm(`"${s.label}" 탭과 그 안의 글을 전부 지울까?`)) {
                await api.deleteSection(s.id); onChanged()
              }
            }}>×</button>
          </div>
        ))}

        <div className="quick-add" style={{ marginTop: 10 }}>
          <input type="text" placeholder="새 탭 이름" value={newLabel}
                 onChange={e => setNewLabel(e.target.value)} />
          <select value={newKind} onChange={e => setNewKind(e.target.value as SectionKind)}
                  style={{ width: 104 }}>
            {CREATABLE_KINDS.map(k => <option key={k} value={k}>{KIND_LABEL[k]}</option>)}
          </select>
          <button className="btn" onClick={addSection} disabled={!newLabel.trim()}>추가</button>
        </div>
      </section>

      <section className="block">
        <div className="news-title">백업</div>
        <p className="k soft" style={{ lineHeight: 1.7 }}>
          전부 파일 하나로 받아둔다. 서버에 무슨 일이 생겨도 이건 손에 남는다.
        </p>
        <button className="btn" onClick={async () => {
          api.downloadJson(
            `minihompy-${me.handle}-${todayKey()}.json`,
            await api.exportBackup(me.id),
          )
        }}>내 기록 전부 내려받기</button>
      </section>
    </div>
  )
}
