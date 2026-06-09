'use client'
import { useEffect, useState } from 'react'
import AuthGuard from '@/components/AuthGuard'
import { fetchCampaigns, Campaign } from '@/lib/api'
import Link from 'next/link'

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])

  useEffect(() => {
    fetchCampaigns().then(setCampaigns).catch(console.error)
  }, [])

  return (
    <AuthGuard>
      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>Campagnes</h1>
          <Link href="/campaigns/create"><button className="btn btn-primary">+ Nouvelle campagne</button></Link>
        </div>

        <table style={{ marginTop: '1rem' }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Enseigne</th>
              <th>Annonceur</th>
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
                <td>{c.id}</td>
                <td>{c.shop_name}</td>
                <td>{c.advertiser}</td>
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
