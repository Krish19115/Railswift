const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

export type Tokens = { access: string; refresh: string }
export type Station = { code: string; name: string; city: string; state: string }
export type TrainMatch = {
  train: { number: string; name: string; is_demo: boolean }
  from: { station: string; name: string; departure_time: string | null }
  to: { station: string; name: string; arrival_time: string | null }
  departure_at: string | null
  arrival_at: string | null
  duration_minutes: number | null
  journey_date: string
}
export type SavedJourney = {
  id: number
  label: string
  source_station: Station
  destination_station: Station
  journey_date: string | null
  preferred_class: string
  quota: string
  is_favorite: boolean
}

export type HealthResponse = {
  status: 'ok' | 'degraded'
  database: 'ok' | 'unavailable'
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health/`)
  const payload = (await response.json()) as HealthResponse
  if (!response.ok && response.status !== 503) {
    throw new Error(`API returned ${response.status}`)
  }
  return payload
}

let accessToken = sessionStorage.getItem('railswift.access')
let refreshToken = sessionStorage.getItem('railswift.refresh')

export function saveTokens(tokens: Tokens) {
  accessToken = tokens.access
  refreshToken = tokens.refresh
  sessionStorage.setItem('railswift.access', tokens.access)
  sessionStorage.setItem('railswift.refresh', tokens.refresh)
}

export async function clearTokens() {
  if (accessToken && refreshToken) {
    await apiRequest('/auth/logout/', {
      method: 'POST',
      body: JSON.stringify({ refresh: refreshToken }),
    }).catch(() => undefined)
  }
  accessToken = null
  refreshToken = null
  sessionStorage.removeItem('railswift.access')
  sessionStorage.removeItem('railswift.refresh')
}

export function hasSession() {
  return Boolean(accessToken)
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Content-Type', 'application/json')
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
  const payload = response.status === 204 ? null : await response.json().catch(() => null)
  if (!response.ok) {
    const fields = payload && typeof payload === 'object' ? Object.values(payload) : []
    const firstFieldError = fields.flatMap((value) => Array.isArray(value) ? value : [value]).find((value) => typeof value === 'string')
    const detail = payload && typeof payload === 'object' && 'detail' in payload
      ? String(payload.detail)
      : typeof firstFieldError === 'string' ? firstFieldError : `Request failed (${response.status})`
    throw new Error(detail)
  }
  return payload as T
}

export async function searchStations(query: string) {
  const params = new URLSearchParams({ search: query })
  return apiRequest<Station[]>(`/stations/?${params}`)
}

export async function searchTrains(source: string, destination: string, date: string) {
  const params = new URLSearchParams({ from: source, to: destination, date })
  return apiRequest<{ results: TrainMatch[]; count: number; notice: string }>(`/trains/between/?${params}`)
}

export async function getSavedJourneys() {
  return apiRequest<SavedJourney[]>('/saved-journeys/')
}

export async function createSavedJourney(source: string, destination: string, date: string) {
  return apiRequest<SavedJourney>('/saved-journeys/', {
    method: 'POST',
    body: JSON.stringify({ source_code: source, destination_code: destination, journey_date: date }),
  })
}
