'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import AuthGuard from '@/components/AuthGuard'
import PageHeader from '@/components/PageHeader'
import StatusBadge from '@/components/StatusBadge'
import ActionMenu from '@/components/ActionMenu'
import ConfirmDialog from '@/components/ConfirmDialog'
import { fetchCampaigns, deleteCampaign, patchCampaignStatus, Campaign } from '@/lib/api'

export default function CampaignsPage() {
  const router = useRouter()
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [error, setError] = useState('')

  const load = () => {
    fetchCampaigns().then(setCampaigns).catch(() => setError('Erreur de chargement'))
  }
  useEffect(() => { load() }, [])

  const handleToggle = async (id: number, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'active' ? 'paused' : 'active'
      await patchCampaignStatus(id, newStatus)
      load()
    } catch { setError('Erreur lors du changement de statut') }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await deleteCampaign(deleteId)
      setDeleteId(null)
      load()
    } catch { setError('Erreur lors de la suppression') }
  }

  return (
    <AuthGuard>
      <div className="container">
        <PageHeader title="Campagnes" actionLabel="Nouvelle campagne" actionHref="/campaigns/create" />

        {error && <div style={{ background: '#fce8e6', color: '#c5221f', padding: '0.75rem', borderRadius: 8, fontSize: '0.85rem', marginBottom: '1rem' }}>{error}</div>}

        <table>
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
              <th></th>
            </tr>
          </thead>
          <tbody>
            {campaigns.map(c => (
              <tr key={c.id} style={{ cursor: 'pointer' }} onClick={() => router.push(`/campaigns/${c.id}`)}>
                <td>{c.id}</td>
                <td style={{ fontWeight: 500 }}>{c.shop_name}</td>
                <td>{c.advertiser}</td>
                <td>{c.zone}</td>
                <td>{(c.budget_cents / 100).toFixed(2)} €</td>
                <td>{(c.bid_cents / 100).toFixed(2)} €</td>
                <td>{c.strategy === 'contextual' ? 'Contextuelle' : 'Flash'}</td>
                <td><StatusBadge status={c.status} /></td>
                <td>{new Date(c.starts_at).toLocaleDateString('fr-FR')}</td>
                <td onClick={e => e.stopPropagation()}>
                  {c.status !== 'expired' && (
                    <ActionMenu items={[
                      { label: 'Voir', icon: 'visibility', onClick: () => router.push(`/campaigns/${c.id}`) },
                      { label: 'Modifier', icon: 'edit', onClick: () => router.push(`/campaigns/${c.id}/edit`) },
                      { label: c.status === 'active' ? 'Mettre en pause' : 'Activer', icon: c.status === 'active' ? 'pause' : 'play_arrow', onClick: () => handleToggle(c.id, c.status) },
                      { label: 'Supprimer', icon: 'delete', danger: true, onClick: () => setDeleteId(c.id) },
                    ]} />
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <ConfirmDialog
          open={deleteId !== null}
          title="Supprimer la campagne"
          message="Êtes-vous sûr de vouloir supprimer cette campagne ? Cette action est irréversible."
          confirmLabel="Supprimer"
          onConfirm={handleDelete}
          onCancel={() => setDeleteId(null)}
        />
      </div>
    </AuthGuard>
  )
}
