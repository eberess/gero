'use client'

interface StatCardProps {
  icon: string
  value: string | number
  label: string
  color?: string
}

export default function StatCard({ icon, value, label, color = '#1a73e8' }: StatCardProps) {
  return (
    <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <div style={{
        width: 52, height: 52, borderRadius: 14,
        background: `${color}10`, display: 'flex',
        alignItems: 'center', justifyContent: 'center',
      }}>
        <span className="material-symbols-outlined" style={{ fontSize: 26, color }}>{icon}</span>
      </div>
      <div>
        <div className="stat-value" style={{ color }}>{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  )
}
