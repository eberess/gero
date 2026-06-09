'use client'
import { useEffect, useState } from 'react'
import { use } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import AuthGuard from '@/components/AuthGuard'
import PageHeader from '@/components/PageHeader'
import StatusBadge from '@/components/StatusBadge'
import ConfirmDialog from '@/components/ConfirmDialog'
import { fetchCampaign, deleteCampaign, patchCampaignStatus } from '@/lib/api'
import { useAuth } from '@/lib/auth'
import type { Campaign } from '@/lib/api'

export default function CampaignDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const campaignId = parseInt(id)
  const router = useRouter()
  const { user } = useAuth()

  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [toggling, setToggling] = useState(false)

  const load = () => {
    fetchCampaign(campaignId)
      .then(setCampaign)
      .catch(() => setError('Campagne introuvable'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleToggleStatus = async () => {
    if (!campaign || toggling) return
    setToggling(true)
    try {
      const newStatus = campaign.status === 'active' ? 'paused' : 'active'
      const updated = await patchCampaignStatus(campaignId, newStatus)
      setCampaign(updated)
    } catch { setError('Erreur lors du changement de statut') }
    setToggling(false)
  }

  const handleDelete = async () => {
    try {
      await deleteCampaign(campaignId)
      router.push('/campaigns')
    } catch { setError('Erreur lors de la suppression') }
    setDeleteOpen(false)
  }

  if (loading) return <div className="container"><p style={{ color: '#5f6368' }}>Chargement...</p></div>
  if (error && !campaign) return <div className="container"><p style={{ color: '#c5221f' }}>{error}</p></div>
  if (!campaign) return null

  const isOwner = user?.role === 'admin' || (user?.role === 'merchant' && user.shop_name === campaign.shop_name)

  return (
    <AuthGuard>
      <div className="container">
        <PageHeader title={`Campagne #${campaign.id}`} />

        {error && <div style={{ background: '#fce8e6', color: '#c5221f', padding: '0.75rem', borderRadius: 8, fontSize: '0.85rem', marginBottom: '1rem' }}>{error}</div>}

        <div className="card">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div>
              <div className="stat-label">Enseigne</div>
              <div style={{ fontWeight: 600, marginBottom: '1rem' }}>{campaign.shop_name}</div>

              <div className="stat-label">Annonceur</div>
              <div style={{ fontWeight: 600, marginBottom: '1rem' }}>{campaign.advertiser}</div>

              <div className="stat-label">Zone</div>
              <div style={{ fontWeight: 600, marginBottom: '1rem' }}>{campaign.zone}</div>

              <div className="stat-label">Mots-clés</div>
              <div style={{ fontWeight: 600, marginBottom: '1rem' }}>{campaign.keywords || '—'}</div>

              <div className="stat-label">Plafond quotidien</div>
              <div style={{ fontWeight: 600, marginBottom: '1rem' }}>{(campaign.daily_max_cents / 100).toFixed(2)} €</div>
            </div>
            <div>
              <div className="stat-label">Statut</div>
              <div style={{ marginBottom: '1rem' }}><StatusBadge status={campaign.status} /></div>

              <div className="stat-label">Budget total</div>
              <div style={{ fontWeight: 600, marginBottom: '1rem' }}>{(campaign.budget_cents / 100).toFixed(2)} €</div>

              <div className="stat-label">Enchère</div>
              <div style={{ fontWeight: 600, marginBottom: '1rem' }}>{(campaign.bid_cents / 100).toFixed(2)} €</div>

              <div className="stat-label">Stratégie</div>
              <div style={{ fontWeight: 600, marginBottom: '1rem' }}>{campaign.strategy === 'contextual' ? 'Contextuelle' : 'Flash (anti-gaspillage)'}</div>

              <div className="stat-label">Début</div>
              <div style={{ fontWeight: 600, marginBottom: '1rem' }}>{new Date(campaign.starts_at).toLocaleDateString('fr-FR')}</div>

              {campaign.ends_at && (
                <>
                  <div className="stat-label">Fin</div>
                  <div style={{ fontWeight: 600, marginBottom: '1rem' }}>{new Date(campaign.ends_at).toLocaleDateString('fr-FR')}</div>
                </>
              )}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid #e8eaed' }}>
            {campaign.status !== 'expired' && isOwner && (
              <button className="btn btn-outline" onClick={handleToggleStatus} disabled={toggling}>
                <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                  {campaign.status === 'active' ? 'pause' : 'play_arrow'}
                </span>
                {campaign.status === 'active' ? 'Mettre en pause' : 'Activer'}
              </button>
            )}
            {isOwner && (
              <Link href={`/campaigns/${campaign.id}/edit`}>
                <button className="btn btn-outline">
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>edit</span>
                  Modifier
                </button>
              </Link>
            )}
            {isOwner && (
              <button className="btn btn-danger" onClick={() => setDeleteOpen(true)}>
                <span className="material-symbols-outlined" style={{ fontSize: 18 }}>delete</span>
                Supprimer
              </button>
            )}
            <Link href="/campaigns"><button className="btn btn-outline">Retour</button></Link>
          </div>
        </div>

        <ConfirmDialog
          open={deleteOpen}
          title="Supprimer la campagne"
          message={`Êtes-vous sûr de vouloir supprimer la campagne #${campaign.id} chez ${campaign.shop_name} ? Cette action est irréversible.`}
          confirmLabel="Supprimer"
          onConfirm={handleDelete}
          onCancel={() => setDeleteOpen(false)}
        />
      </div>
    </AuthGuard>
  )
}
