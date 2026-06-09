'use client'
import { useState, useRef, useEffect } from 'react'

interface ActionItem {
  label: string
  icon: string
  onClick: () => void
  danger?: boolean
}

interface ActionMenuProps {
  items: ActionItem[]
}

export default function ActionMenu({ items }: ActionMenuProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button
        className="btn-ghost"
        style={{ padding: '0.3rem 0.5rem', minWidth: 32, fontSize: 18, lineHeight: 1 }}
        onClick={() => setOpen(!open)}
      >
        ⋯
      </button>
      {open && (
        <div style={{
          position: 'absolute', right: 0, top: '100%', marginTop: 4,
          background: 'white', borderRadius: 12, boxShadow: '0 4px 20px rgba(0,0,0,0.12)',
          minWidth: 180, padding: '0.4rem', zIndex: 50,
        }}>
          {items.map((item, i) => (
            <button
              key={i}
              onClick={() => { item.onClick(); setOpen(false) }}
              style={{
                display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%',
                padding: '0.5rem 0.75rem', border: 'none', background: 'none',
                borderRadius: 8, cursor: 'pointer', fontSize: '0.85rem',
                color: item.danger ? '#c5221f' : '#202124',
              }}
              onMouseEnter={e => (e.currentTarget.style.background = '#f8f9fa')}
              onMouseLeave={e => (e.currentTarget.style.background = 'none')}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 18, color: item.danger ? '#c5221f' : '#5f6368' }}>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
