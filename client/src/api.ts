// Transport layer for the FastAPI backend. In dev, VITE_API_BASE_URL is unset,
// so requests use relative /api paths and the Vite dev server proxies them to
// http://localhost:8000 (see vite.config.ts). In the deployed build it's set to
// the Cloud Run URL, making the calls absolute + cross-origin (the API's CORS
// allowlist must then include this frontend's origin).

import type { ChampionDict, DraftStateRequest, RecommendationResponse } from './types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function throwApiError(res: Response): Promise<never> {
  let message = `Request failed with status ${res.status}`
  try {
    const body = await res.json()
    if (typeof body?.detail === 'string') message = body.detail
  } catch {
    // non-JSON error body; keep the generic message
  }
  throw new ApiError(res.status, message)
}

export async function fetchChampions(): Promise<ChampionDict> {
  const res = await fetch(`${API_BASE}/api/champions`)
  if (!res.ok) await throwApiError(res)
  return res.json()
}

export async function fetchRecommendations(
  req: DraftStateRequest,
  signal: AbortSignal,
): Promise<RecommendationResponse> {
  const res = await fetch(`${API_BASE}/api/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    signal,
  })
  if (!res.ok) await throwApiError(res)
  return res.json()
}
