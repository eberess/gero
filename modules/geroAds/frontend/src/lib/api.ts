const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function authHeaders(): HeadersInit {
  if (typeof window === 'undefined') return {}
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export interface User {
  id: number
  email: string
  company: string
  role: 'admin' | 'merchant'
  shop_name: string | null
}

export interface Campaign {
  id: number
  advertiser: string
  shop_name: string
  zone: string
  keywords: string
  budget_cents: number
  bid_cents: number
  strategy: string
  status: string
  daily_max_cents: number
  starts_at: string
  ends_at: string | null
  created_at: string
}

export interface Shop {
  id: number
  name: string
  zone: string
  category: string
  description: string
  tags: string
  lat: number | null
  lon: number | null
  is_artisan: boolean
}

export interface Stats {
  total_campaigns: number
  active_campaigns: number
  total_impressions: number
  total_budget_eur: number
}

export async function login(email: string, password: string): Promise<{ access_token: string; user: User }> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) throw new Error('Email ou mot de passe invalide')
  const data = await res.json()
  localStorage.setItem('token', data.access_token)
  localStorage.setItem('user', JSON.stringify(data.user))
  return data
}

export function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

export function getStoredUser(): User | null {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem('user')
  return raw ? JSON.parse(raw) : null
}

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('token')
}

export async function fetchMe(): Promise<User> {
  const res = await fetch(`${API_BASE}/api/auth/me`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Non authentifié')
  return res.json()
}

export async function fetchCampaigns(): Promise<Campaign[]> {
  const res = await fetch(`${API_BASE}/api/ads/campaigns`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Failed to fetch campaigns')
  return res.json()
}

export async function createCampaign(data: Record<string, unknown>): Promise<Campaign> {
  const res = await fetch(`${API_BASE}/api/ads/campaign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to create campaign')
  return res.json()
}

export async function fetchCampaign(id: number): Promise<Campaign> {
  const res = await fetch(`${API_BASE}/api/ads/campaign/${id}`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Campagne introuvable')
  return res.json()
}

export async function updateCampaign(id: number, data: Record<string, unknown>): Promise<Campaign> {
  const res = await fetch(`${API_BASE}/api/ads/campaign/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Échec de la mise à jour')
  return res.json()
}

export async function deleteCampaign(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/api/ads/campaign/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error('Échec de la suppression')
}

export async function patchCampaignStatus(id: number, status: string): Promise<Campaign> {
  const res = await fetch(`${API_BASE}/api/ads/campaign/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ status }),
  })
  if (!res.ok) throw new Error('Échec du changement de statut')
  return res.json()
}

export async function createShop(data: Record<string, unknown>): Promise<Shop> {
  const res = await fetch(`${API_BASE}/api/shops`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to create shop')
  return res.json()
}

export async function fetchShops(): Promise<Shop[]> {
  const res = await fetch(`${API_BASE}/api/shops`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Failed to fetch shops')
  return res.json()
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/api/ads/stats`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Failed to fetch stats')
  return res.json()
}

export async function fetchMerchantStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/api/ads/merchant/stats`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Failed to fetch stats')
  return res.json()
}

export async function fetchUsers(): Promise<User[]> {
  const res = await fetch(`${API_BASE}/api/users`, { headers: authHeaders() })
  if (!res.ok) throw new Error('Failed to fetch users')
  return res.json()
}
