'use client'
import { useEffect, useState } from 'react'
import AuthGuard from '@/components/AuthGuard'
import { fetchCampaigns, fetchStats, fetchUsers, Campaign, Stats, User } from '@/lib/api'

export default function AdminDashboard() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [users, setUsers] = useState<User[]>([])

  useEffect(() => {
    fetchCampaigns().then(setCampaigns).catch(console.error)
    fetchStats().then(setStats).catch(console.error)
    fetchUsers().then(setUsers).catch(console.error)
  }, [])

  return (
    <AuthGuard role="admin">
      <div className="container">
        <h1>Administration ADP</h1>

        {stats && (
          <div className="grid">
            <div className="card">
              <div className="stat-value">{stats.active_campaigns}</div>
              <div className="stat-label">Campagnes actives</div>
            </div>
            <div className="card">
              <div className="stat-value">{stats.total_campaigns}</div>
              <div className="stat-label">Campagnes totales</div>
            </div>
            <div className="card">
              <div className="stat-value">{stats.total_impressions}</div>
              <div className="stat-label">Impressions générées</div>
            </div>
            <div className="card">
              <div className="stat-value">{stats.total_budget_eur.toFixed(2)} €</div>
              <div className="stat-label">Budget total engagé</div>
            </div>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '2rem' }}>
          <div>
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
                    <td>{u.email}</td>
                    <td>{u.shop_name || '-'}</td>
                    <td><span className="badge" style={{background: u.role === 'admin' ? '#e8eaf6' : '#fff3e0'}}>{u.role}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div>
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
                  <tr key={c.id}>
                    <td>{c.shop_name}</td>
                    <td>{(c.budget_cents / 100).toFixed(2)} €</td>
                    <td><span className={`badge ${c.status}`}>{c.status}</span></td>
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
