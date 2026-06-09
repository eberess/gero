'use client'
import { useEffect, useState } from 'react'
import AuthGuard from '@/components/AuthGuard'
import PageHeader from '@/components/PageHeader'
import { fetchShops, createShop, Shop } from '@/lib/api'

export default function ShopsPage() {
  const [shops, setShops] = useState<Shop[]>([])
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    name: '',
    zone: 'T2F_Central',
    category: '',
    description: '',
    tags: '',
    lat: '',
    lon: '',
    is_artisan: false,
  })

  const load = () => {
    fetchShops().then(setShops).catch(() => setError('Erreur de chargement'))
  }
  useEffect(() => { load() }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await createShop({
        name: form.name,
        zone: form.zone,
        category: form.category,
        description: form.description,
        tags: form.tags.split(',').map(t => t.trim()).filter(Boolean),
        lat: form.lat ? parseFloat(form.lat) : null,
        lon: form.lon ? parseFloat(form.lon) : null,
        is_artisan: form.is_artisan,
      })
      setShowForm(false)
      setForm({ name: '', zone: 'T2F_Central', category: '', description: '', tags: '', lat: '', lon: '', is_artisan: false })
      load()
    } catch { setError('Erreur lors de la création') }
  }

  return (
    <AuthGuard role="admin">
      <div className="container">
        <PageHeader title="Commerces" actionLabel="Ajouter un commerce" onAction={() => setShowForm(!showForm)} />

        {error && <div style={{ background: '#fce8e6', color: '#c5221f', padding: '0.75rem', borderRadius: 8, fontSize: '0.85rem', marginBottom: '1rem' }}>{error}</div>}

        {showForm && (
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <h2>Nouveau commerce</h2>
            <form onSubmit={handleSubmit}>
              <label>Nom <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} required /></label>
              <label>Zone
                <select value={form.zone} onChange={e => setForm({...form, zone: e.target.value})}>
                  <option value="all">Tout le terminal</option>
                  <option value="T2F_North">T2F Nord</option>
                  <option value="T2F_South">T2F Sud</option>
                  <option value="T2F_Central">T2F Central</option>
                  <option value="T2F_Satellite">T2F Satellite</option>
                </select>
              </label>
              <label>Catégorie <input value={form.category} onChange={e => setForm({...form, category: e.target.value})} placeholder="ex: restauration, boutique" /></label>
              <label>Description <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} /></label>
              <label>Tags (séparés par des virgules) <input value={form.tags} onChange={e => setForm({...form, tags: e.target.value})} placeholder="ex: café, rapide, halal" /></label>
              <label>Latitude <input type="number" step="any" value={form.lat} onChange={e => setForm({...form, lat: e.target.value})} /></label>
              <label>Longitude <input type="number" step="any" value={form.lon} onChange={e => setForm({...form, lon: e.target.value})} /></label>
              <label style={{ flexDirection: 'row', gap: '0.5rem' }}>
                <input type="checkbox" checked={form.is_artisan} onChange={e => setForm({...form, is_artisan: e.target.checked})} style={{ width: 'auto' }} />
                Artisan / commerce local
              </label>
              <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-start' }}>Créer le commerce</button>
            </form>
          </div>
        )}

        <div className="card">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nom</th>
                <th>Zone</th>
                <th>Catégorie</th>
                <th>Artisan</th>
                <th>Tags</th>
              </tr>
            </thead>
            <tbody>
              {shops.map(s => (
                <tr key={s.id}>
                  <td>{s.id}</td>
                  <td style={{ fontWeight: 500 }}>{s.name}</td>
                  <td>{s.zone}</td>
                  <td>{s.category || '-'}</td>
                  <td>{s.is_artisan ? <span className="badge" style={{background: '#fce8e6', color: '#c5221f'}}>Artisan</span> : '-'}</td>
                  <td style={{ fontSize: '0.8rem' }}>{s.tags || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AuthGuard>
  )
}
