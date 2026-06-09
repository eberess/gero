'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { login as apiLogin } from '@/lib/api'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const { loginUser } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { user } = await apiLogin(email, password)
      loginUser(user)
      router.push('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de connexion')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Connexion</h1>
        <p className="subtitle">GeroAds — Business Portal</p>

        {error && <div className="login-error">{error}</div>}

        <form onSubmit={handleSubmit} style={{ marginTop: '1rem' }}>
          <label>
            Email
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="ex: admin@adp.fr" required />
          </label>
          <label>
            Mot de passe
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
          </label>
          <button type="submit" className="btn btn-primary" style={{ justifyContent: 'center', marginTop: '0.5rem' }} disabled={loading}>
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        <div style={{ marginTop: '1.5rem', fontSize: '0.8rem', color: '#999', textAlign: 'center' }}>
          <p>Comptes de démonstration :</p>
          <p style={{ marginTop: '0.3rem' }}>admin@adp.fr / admin123</p>
          <p>contact@paul bakery.fr / merchant123</p>
          <p>contact@ladycafe.fr / merchant123</p>
        </div>
      </div>
    </div>
  )
}
