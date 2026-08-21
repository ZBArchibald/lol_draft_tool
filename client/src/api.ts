// Transport layer for the FastAPI backend. Paths are relative; the Vite dev
// server proxies /api to http://localhost:8000 (see vite.config.ts).

import type { ChampionDict, DraftStateRequest, RecommendationResponse } from './types'

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
  const res = await fetch('/api/champions')
  if (!res.ok) await throwApiError(res)
  return res.json()
}

export async function fetchRecommendations(
  req: DraftStateRequest,
  signal: AbortSignal,
): Promise<RecommendationResponse> {
  const res = await fetch('/api/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    signal,
  })
  if (!res.ok) await throwApiError(res)
  return res.json()
}
