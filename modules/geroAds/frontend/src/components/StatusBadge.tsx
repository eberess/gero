'use client'

const STATUS_LABELS: Record<string, string> = {
  active: 'Active',
  paused: 'En pause',
  expired: 'Expirée',
}

export default function StatusBadge({ status }: { status: string }) {
  return <span className={`badge ${status}`}>{STATUS_LABELS[status] || status}</span>
}
