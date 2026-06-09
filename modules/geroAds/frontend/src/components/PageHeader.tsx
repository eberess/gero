'use client'
import Link from 'next/link'

interface PageHeaderProps {
  title: string
  actionLabel?: string
  actionHref?: string
  onAction?: () => void
}

export default function PageHeader({ title, actionLabel, actionHref, onAction }: PageHeaderProps) {
  const btn = actionLabel ? (
    <button className="btn btn-primary" onClick={onAction}>
      <span className="material-symbols-outlined" style={{ fontSize: 18 }}>add</span>
      {actionLabel}
    </button>
  ) : null

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
      <h1 style={{ margin: 0 }}>{title}</h1>
      {actionHref ? <Link href={actionHref}>{btn}</Link> : btn}
    </div>
  )
}
