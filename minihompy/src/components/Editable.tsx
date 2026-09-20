import { useEffect, useRef, useState } from 'react'

/**
 * 눌러서 그 자리에서 고친다.
 *
 * 지금까지는 만들기와 지우기만 있어서 오타 하나를 고치려면 지우고 다시
 * 써야 했다. 다시 쓰는 비용이 고치는 비용보다 크면 사람은 틀린 채로 둔다.
 * 그래서 편집 화면을 따로 띄우지 않고 글자 위에서 바로 받는다.
 */
export default function Editable({
  value, onSave, multiline = false, placeholder = '', disabled = false, className = '',
}: {
  value: string
  onSave: (next: string) => Promise<void> | void
  multiline?: boolean
  placeholder?: string
  disabled?: boolean
  className?: string
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)
  const ref = useRef<HTMLInputElement & HTMLTextAreaElement>(null)

  useEffect(() => { setDraft(value) }, [value])
  useEffect(() => { if (editing) { ref.current?.focus(); ref.current?.select() } }, [editing])

  async function commit() {
    setEditing(false)
    const next = draft.trim()
    if (next === value.trim()) return
    await onSave(next)
  }

  if (disabled) {
    return <span className={className}>{value || placeholder}</span>
  }

  if (!editing) {
    return (
      <button className={`editable ${className}`} onClick={() => setEditing(true)}
              title="눌러서 고치기">
        {value || <span className="ph">{placeholder}</span>}
      </button>
    )
  }

  const common = {
    ref, value: draft, placeholder,
    onChange: (e: { target: { value: string } }) => setDraft(e.target.value),
    onBlur: commit,
  }

  return multiline
    ? <textarea {...common} rows={4} className="editing"
                onKeyDown={e => { if (e.key === 'Escape') { setDraft(value); setEditing(false) } }} />
    : <input {...common} type="text" className="editing"
             onKeyDown={e => {
               if (e.key === 'Enter') void commit()
               if (e.key === 'Escape') { setDraft(value); setEditing(false) }
             }} />
}
