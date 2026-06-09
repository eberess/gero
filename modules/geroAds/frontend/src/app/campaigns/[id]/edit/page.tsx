'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { use } from 'react'
import AuthGuard from '@/components/AuthGuard'
import PageHeader from '@/components/PageHeader'
import { fetchCampaign, updateCampaign } from '@/lib/api'

export default function EditCampaignPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const campaignId = parseInt(id)
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    advertiser: '',
    shop_name: '',
    zone: 'T2F_Central',
    keywords: '',
    budget_cents: 10000,
    bid_cents: 50,
    strategy: 'contextual',
    daily_max_cents: 2000,
    starts_at: '',
    ends_at: '',
  })

  useEffect(() => {
    fetchCampaign(campaignId)
      .then(c => setForm({
        advertiser: c.advertiser,
        shop_name: c.shop_name,
        zone: c.zone,
        keywords: c.keywords,
        budget_cents: c.budget_cents,
        bid_cents: c.bid_cents,
        strategy: c.strategy === 'flash' ? 'flash' : 'contextual',
        daily_max_cents: c.daily_max_cents,
        starts_at: c.starts_at.slice(0, 16),
        ends_at: c.ends_at ? c.ends_at.slice(0, 16) : '',
      }))
      .catch(() => setError('Campagne introuvable'))
      .finally(() => setLoading(false))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      await updateCampaign(campaignId, {
        ...form,
        keywords: form.keywords.split(',').map(k => k.trim()).filter(Boolean),
        starts_at: new Date(form.starts_at).toISOString(),
        ends_at: form.ends_at ? new Date(form.ends_at).toISOString() : null,
      })
      router.push(`/campaigns/${campaignId}`)
    } catch { setError('Erreur lors de la sauvegarde') }
    setSaving(false)
  }

  if (loading) return <div className="container"><p style={{ color: '#5f6368' }}>Chargement...</p></div>

  return (
    <AuthGuard>
      <div className="container">
        <PageHeader title={`Modifier la campagne #${campaignId}`} />

        {error && <div style={{ background: '#fce8e6', color: '#c5221f', padding: '0.75rem', borderRadius: 8, fontSize: '0.85rem', marginBottom: '1rem' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <label>Annonceur <input value={form.advertiser} onChange={e => setForm({...form, advertiser: e.target.value})} placeholder="Nom de l'annonceur" /></label>
          <label>Enseigne <input value={form.shop_name} onChange={e => setForm({...form, shop_name: e.target.value})} placeholder="Nom de l'enseigne" required /></label>
          <label>Zone
            <select value={form.zone} onChange={e => setForm({...form, zone: e.target.value})}>
              <option value="all">Tout le terminal</option>
              <option value="T2F_North">T2F Nord</option>
              <option value="T2F_South">T2F Sud</option>
              <option value="T2F_Central">T2F Central</option>
              <option value="T2F_Satellite">T2F Satellite</option>
            </select>
          </label>
          <label>Mots-clés (séparés par des virgules) <textarea value={form.keywords} onChange={e => setForm({...form, keywords: e.target.value})} placeholder="ex: café, croissant, petit-déjeuner" /></label>
          <label>Budget total (centimes) <input type="number" value={form.budget_cents} onChange={e => setForm({...form, budget_cents: +e.target.value})} /></label>
          <label>Enchère par impression (centimes) <input type="number" value={form.bid_cents} onChange={e => setForm({...form, bid_cents: +e.target.value})} /></label>
          <label>Stratégie
            <select value={form.strategy} onChange={e => setForm({...form, strategy: e.target.value})}>
              <option value="contextual">Contextuelle</option>
              <option value="flash">Flash (anti-gaspillage)</option>
            </select>
          </label>
          <label>Début <input type="datetime-local" value={form.starts_at} onChange={e => setForm({...form, starts_at: e.target.value})} /></label>
          <label>Fin (optionnelle) <input type="datetime-local" value={form.ends_at} onChange={e => setForm({...form, ends_at: e.target.value})} /></label>
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Sauvegarde...' : 'Enregistrer'}</button>
          </div>
        </form>
      </div>
    </AuthGuard>
  )
}
