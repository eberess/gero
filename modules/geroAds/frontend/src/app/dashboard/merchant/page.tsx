'use client'
import { useEffect, useState } from 'react'
import AuthGuard from '@/components/AuthGuard'
import { fetchCampaigns, fetchMerchantStats, Campaign, Stats } from '@/lib/api'
import Link from 'next/link'

export default function MerchantDashboard() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    fetchCampaigns().then(setCampaigns).catch(console.error)
    fetchMerchantStats().then(setStats).catch(console.error)
  }, [])

  return (
    <AuthGuard role="merchant">
      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>Mon tableau de bord</h1>
          <Link href="/campaigns/create"><button className="btn btn-primary">+ Nouvelle campagne</button></Link>
        </div>

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
              <div className="stat-label">Impressions</div>
            </div>
            <div className="card">
              <div className="stat-value">{stats.total_budget_eur.toFixed(2)} €</div>
              <div className="stat-label">Budget total</div>
            </div>
          </div>
        )}

        <h2 style={{ marginTop: '2rem' }}>Mes campagnes</h2>
        <table>
          <thead>
            <tr>
              <th>Enseigne</th>
              <th>Zone</th>
              <th>Budget</th>
              <th>Enchère</th>
              <th>Stratégie</th>
              <th>Statut</th>
              <th>Début</th>
            </tr>
          </thead>
          <tbody>
            {campaigns.map(c => (
              <tr key={c.id}>
                <td>{c.shop_name}</td>
                <td>{c.zone}</td>
                <td>{(c.budget_cents / 100).toFixed(2)} €</td>
                <td>{(c.bid_cents / 100).toFixed(2)} €</td>
                <td>{c.strategy}</td>
                <td><span className={`badge ${c.status}`}>{c.status}</span></td>
                <td>{new Date(c.starts_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AuthGuard>
  )
}
