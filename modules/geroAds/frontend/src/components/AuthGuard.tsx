'use client'
import { useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'

export default function AuthGuard({ children, role }: { children: ReactNode; role?: string }) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return
    if (!user) router.replace('/login')
    else if (role && user.role !== role) router.replace('/dashboard')
  }, [user, loading, role, router])

  if (loading) return <div className="container" style={{textAlign:'center',padding:'4rem'}}>Chargement...</div>
  if (!user) return null
  if (role && user.role !== role) return null
  return <>{children}</>
}
