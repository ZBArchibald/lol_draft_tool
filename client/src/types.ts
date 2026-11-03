// Mirrors of the backend Pydantic schemas (backend/api/schemas.py).

export const POSITIONS = ['top', 'jungle', 'mid', 'bot', 'support'] as const
export type Position = (typeof POSITIONS)[number]

export const POSITION_LABELS: Record<Position, string> = {
  top: 'TOP',
  jungle: 'JUNGLE',
  mid: 'MID',
  bot: 'BOT',
  support: 'SUPPORT',
}

// Compact labels for narrow screens.
export const POSITION_SHORT_LABELS: Record<Position, string> = {
  top: 'TOP',
  jungle: 'JG',
  mid: 'MID',
  bot: 'BOT',
  support: 'SUP',
}

export interface ChampionInfo {
  name: string
  sprite_url: string
  // Positions the champion is viable in (same >=20% role-share rule the
  // recommender uses). Empty until the champion has ingested games.
  roles: Position[]
}

// GET /api/champions — JSON object keys arrive as stringified ints;
// Record<number, ...> still indexes correctly since JS object keys are strings.
export type ChampionDict = Record<number, ChampionInfo>

export interface DraftStateRequest {
  position: Position
  banned: number[]
  allies: number[]
  enemies: number[]
}

export interface ChampionRecommendation {
  champion: number
  // 0-1 float from an unweighted matchup average — a relative score,
  // not a calibrated win probability.
  win_chance: number
}

export interface RecommendationResponse {
  recommendations: ChampionRecommendation[]
}

// Client-only draft-board types.

export type Team = 'blue' | 'red'
export type SlotKind = 'pick' | 'ban'

export interface SlotRef {
  team: Team
  kind: SlotKind
  index: number // 0-4 within its row/column
}

export interface Draft {
  bluePicks: (number | null)[]
  redPicks: (number | null)[]
  blueBans: (number | null)[]
  redBans: (number | null)[]
}
