'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AuthGuard from '@/components/AuthGuard'
import StatCard from '@/components/StatCard'
import StatusBadge from '@/components/StatusBadge'
import PageHeader from '@/components/PageHeader'
import { fetchCampaigns, fetchStats, fetchUsers, Campaign, Stats, User } from '@/lib/api'

export default function AdminDashboard() {
  const router = useRouter()
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [users, setUsers] = useState<User[]>([])

  useEffect(() => {
    fetchCampaigns().then(setCampaigns).catch(console.error)
    fetchStats().then(setStats).catch(console.error)
    fetchUsers().then(setUsers).catch(console.error)
  }, [])

  const activeCount = campaigns.filter(c => c.status === 'active').length
  const totalBudget = campaigns.reduce((s, c) => s + c.budget_cents, 0) / 100

  return (
    <AuthGuard role="admin">
      <div className="container">
        <PageHeader title="Administration ADP" />

        {stats && (
          <div className="grid" style={{ marginBottom: '2rem' }}>
            <StatCard icon="campaign" value={stats.active_campaigns} label="Campagnes actives" color="#1e7e34" />
            <StatCard icon="list_alt" value={stats.total_campaigns} label="Campagnes totales" />
            <StatCard icon="visibility" value={stats.total_impressions} label="Impressions générées" color="#7b1fa2" />
            <StatCard icon="account_balance" value={`${stats.total_budget_eur.toFixed(2)} €`} label="Budget total engagé" color="#ea8600" />
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
          <div className="card">
            <h2>Commerçants</h2>
            <table>
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Enseigne</th>
                  <th>Rôle</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td style={{ fontSize: '0.8rem' }}>{u.email}</td>
                    <td>{u.shop_name || '-'}</td>
                    <td>
                      <span className="badge" style={{
                        background: u.role === 'admin' ? '#e8eaf6' : '#fff3e0',
                        color: u.role === 'admin' ? '#283593' : '#e65100',
                      }}>
                        {u.role === 'admin' ? 'ADP' : 'Commerçant'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card">
            <h2>Dernières campagnes</h2>
            <table>
              <thead>
                <tr>
                  <th>Enseigne</th>
                  <th>Budget</th>
                  <th>Statut</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.slice(0, 10).map(c => (
                  <tr key={c.id} style={{ cursor: 'pointer' }} onClick={() => router.push(`/campaigns/${c.id}`)}>
                    <td style={{ fontWeight: 500 }}>{c.shop_name}</td>
                    <td>{(c.budget_cents / 100).toFixed(2)} €</td>
                    <td><StatusBadge status={c.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AuthGuard>
  )
}
