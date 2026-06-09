'use client'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { logout as apiLogout } from '@/lib/api'

export default function Navbar() {
  const { user, logout } = useAuth()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    apiLogout()
    router.push('/')
  }

  if (!user) {
    return (
      <header className="header">
        <div className="header-left">
          <Link href="/" className="logo">GeroAds</Link>
          <nav>
            <Link href="/ad-solutions">Solutions</Link>
            <Link href="/analytics">Analytics</Link>
          </nav>
        </div>
        <div className="header-right">
          <Link href="/login"><button className="btn-ghost">Connexion</button></Link>
        </div>
      </header>
    )
  }

  return (
    <header className="header">
      <div className="header-left">
        <Link href="/" className="logo">GeroAds</Link>
        <nav>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/campaigns">Campagnes</Link>
          {user.role === 'admin' && <Link href="/dashboard/admin">Admin</Link>}
        </nav>
      </div>
      <div className="header-right">
        <span className="user-email">{user.email}</span>
        <span className="badge" style={{background:user.role==='admin'?'#e6f4ea':'#f0f6ff',color:user.role==='admin'?'#1e7e34':'#1a73e8'}}>
          {user.role === 'admin' ? 'ADP' : 'Commerçant'}
        </span>
        <button className="btn-ghost" onClick={handleLogout}>Déconnexion</button>
      </div>
    </header>
  )
}
