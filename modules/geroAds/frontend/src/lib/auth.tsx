'use client'
import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, fetchMe, logout as apiLogout, getStoredUser } from './api'

interface AuthContextType {
  user: User | null
  loading: boolean
  loginUser: (user: User) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  loginUser: () => {},
  logout: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = getStoredUser()
    if (stored) {
      fetchMe()
        .then(setUser)
        .catch(() => { setUser(null); apiLogout() })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const loginUser = (u: User) => setUser(u)
  const logout = () => { setUser(null); apiLogout() }

  return (
    <AuthContext.Provider value={{ user, loading, loginUser, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
