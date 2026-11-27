const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

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
