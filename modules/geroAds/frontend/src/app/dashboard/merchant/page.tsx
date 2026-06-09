'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AuthGuard from '@/components/AuthGuard'
import StatCard from '@/components/StatCard'
import StatusBadge from '@/components/StatusBadge'
import PageHeader from '@/components/PageHeader'
import { fetchCampaigns, fetchMerchantStats, Campaign, Stats } from '@/lib/api'

export default function MerchantDashboard() {
  const router = useRouter()
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    fetchCampaigns().then(setCampaigns).catch(console.error)
    fetchMerchantStats().then(setStats).catch(console.error)
  }, [])

  return (
    <AuthGuard role="merchant">
      <div className="container">
        <PageHeader title="Mon tableau de bord" actionLabel="Nouvelle campagne" actionHref="/campaigns/create" />

        {stats && (
          <div className="grid" style={{ marginBottom: '2rem' }}>
            <StatCard icon="campaign" value={stats.active_campaigns} label="Campagnes actives" color="#1e7e34" />
            <StatCard icon="list_alt" value={stats.total_campaigns} label="Campagnes totales" />
            <StatCard icon="visibility" value={stats.total_impressions} label="Impressions" color="#7b1fa2" />
            <StatCard icon="account_balance" value={`${stats.total_budget_eur.toFixed(2)} €`} label="Budget total" color="#ea8600" />
          </div>
        )}

        <div className="card">
          <h2>Mes campagnes</h2>
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
                <tr key={c.id} style={{ cursor: 'pointer' }} onClick={() => router.push(`/campaigns/${c.id}`)}>
                  <td style={{ fontWeight: 500 }}>{c.shop_name}</td>
                  <td>{c.zone}</td>
                  <td>{(c.budget_cents / 100).toFixed(2)} €</td>
                  <td>{(c.bid_cents / 100).toFixed(2)} €</td>
                  <td>{c.strategy === 'contextual' ? 'Contextuelle' : 'Flash'}</td>
                  <td><StatusBadge status={c.status} /></td>
                  <td>{new Date(c.starts_at).toLocaleDateString('fr-FR')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AuthGuard>
  )
}
