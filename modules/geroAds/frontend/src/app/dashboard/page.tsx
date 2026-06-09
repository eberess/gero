'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'

export default function DashboardRedirect() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return
    if (!user) router.replace('/login')
    else if (user.role === 'admin') router.replace('/dashboard/admin')
    else router.replace('/dashboard/merchant')
  }, [user, loading, router])

  return <div className="container" style={{textAlign:'center',padding:'4rem'}}>Redirection...</div>
}
