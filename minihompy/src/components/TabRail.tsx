import type { Section } from '../lib/types'

/** PC에선 바인더 옆 세로 탭, 모바일에선 가로 칩. 모양은 CSS가 바꾼다. */
export default function TabRail({ sections, current, onPick, isOwner, onAdd }: {
  sections: Section[]
  current: string
  onPick: (id: string) => void
  isOwner: boolean
  onAdd: () => void
}) {
  return (
    <nav className="tabs" aria-label="섹션">
      <button className={`tab ${current === 'home' ? 'active' : ''}`}
              onClick={() => onPick('home')}>홈</button>
      {sections.map(s => (
        <button key={s.id} className={`tab ${current === s.id ? 'active' : ''}`}
                onClick={() => onPick(s.id)} title={s.label}>
          {s.label}
        </button>
      ))}
      {isOwner && <button className="tab add" onClick={onAdd} title="탭 추가">+</button>}
    </nav>
  )
}
