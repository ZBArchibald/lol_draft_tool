import { useEffect, useMemo, useState } from 'react'
import { ApiError, fetchChampions, fetchRecommendations } from './api'
import type {
  ChampionDict,
  ChampionRecommendation,
  Draft,
  DraftStateRequest,
  Position,
  SlotRef,
} from './types'
import DraftBoard from './components/DraftBoard'
import RoleSelector from './components/RoleSelector'
import './App.css'

const EMPTY_DRAFT: Draft = {
  bluePicks: [null, null, null, null, null],
  redPicks: [null, null, null, null, null],
  blueBans: [null, null, null, null, null],
  redBans: [null, null, null, null, null],
}

const slotArrayKey = (slot: SlotRef): keyof Draft =>
  slot.kind === 'pick'
    ? slot.team === 'blue'
      ? 'bluePicks'
      : 'redPicks'
    : slot.team === 'blue'
      ? 'blueBans'
      : 'redBans'

const nonNull = (ids: (number | null)[]): number[] =>
  ids.filter((id): id is number => id !== null)

// Blue is always the user's team: bluePicks -> allies, redPicks -> enemies.
function buildRequest(draft: Draft, role: Position): DraftStateRequest {
  return {
    position: role,
    banned: [...nonNull(draft.blueBans), ...nonNull(draft.redBans)],
    allies: nonNull(draft.bluePicks),
    enemies: nonNull(draft.redPicks),
  }
}

function errorMessage(err: unknown): string {
  if (err instanceof ApiError) return err.message
  return 'Could not reach the draft API — is the backend running on :8000?'
}

export default function App() {
  // Session-long champion dictionary; fetched once on mount (null = loading).
  const [champions, setChampions] = useState<ChampionDict | null>(null)
  const [championsError, setChampionsError] = useState<string | null>(null)
  const [championsRetry, setChampionsRetry] = useState(0)

  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT)
  const [role, setRole] = useState<Position>('mid')
  const [activeSlot, setActiveSlot] = useState<SlotRef | null>(null)

  const [recs, setRecs] = useState<ChampionRecommendation[] | null>(null)
  const [recsLoading, setRecsLoading] = useState(false)
  const [recsError, setRecsError] = useState<string | null>(null)
  const [recsRetry, setRecsRetry] = useState(0)

  useEffect(() => {
    let cancelled = false
    setChampionsError(null)
    fetchChampions()
      .then((dict) => {
        if (!cancelled) setChampions(dict)
      })
      .catch((err) => {
        if (!cancelled) setChampionsError(errorMessage(err))
      })
    return () => {
      cancelled = true
    }
  }, [championsRetry])

  // Every draft/role mutation fires a fresh request; the cleanup aborts any
  // in-flight one, so rapid clicks never race or show stale results.
  useEffect(() => {
    const controller = new AbortController()
    setRecsLoading(true)
    setRecsError(null)
    fetchRecommendations(buildRequest(draft, role), controller.signal)
      .then((res) => {
        setRecs(res.recommendations)
        setRecsLoading(false)
      })
      .catch((err) => {
        if (err instanceof DOMException && err.name === 'AbortError') return
        setRecsError(errorMessage(err))
        setRecsLoading(false)
      })
    return () => controller.abort()
  }, [draft, role, recsRetry])

  const usedChampionIds = useMemo(() => {
    const all = [
      ...draft.bluePicks,
      ...draft.redPicks,
      ...draft.blueBans,
      ...draft.redBans,
    ]
    return new Set(nonNull(all))
  }, [draft])

  const sameSlot = (a: SlotRef, b: SlotRef) =>
    a.team === b.team && a.kind === b.kind && a.index === b.index

  const handleSlotClick = (slot: SlotRef) => {
    const key = slotArrayKey(slot)
    if (draft[key][slot.index] !== null) {
      // Filled slot: clear it (the champion returns to the grid).
      setDraft((prev) => ({
        ...prev,
        [key]: prev[key].map((id, i) => (i === slot.index ? null : id)),
      }))
      setActiveSlot(null)
    } else if (activeSlot && sameSlot(activeSlot, slot)) {
      setActiveSlot(null)
    } else {
      setActiveSlot(slot)
    }
  }

  const handleChampionClick = (championId: number) => {
    if (!activeSlot || usedChampionIds.has(championId)) return
    const key = slotArrayKey(activeSlot)
    const index = activeSlot.index
    setDraft((prev) => ({
      ...prev,
      [key]: prev[key].map((id, i) => (i === index ? championId : id)),
    }))
    setActiveSlot(null)
  }

  if (championsError) {
    return (
      <div className="fullscreen-state">
        <p className="error-text">{championsError}</p>
        <button onClick={() => setChampionsRetry((n) => n + 1)}>Retry</button>
      </div>
    )
  }

  if (!champions) {
    return (
      <div className="fullscreen-state">
        <p>Loading champions…</p>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>LoL Draft Tool</h1>
        <RoleSelector role={role} onChange={setRole} />
      </header>
      <DraftBoard
        champions={champions}
        draft={draft}
        activeSlot={activeSlot}
        usedChampionIds={usedChampionIds}
        onSlotClick={handleSlotClick}
        onChampionClick={handleChampionClick}
        recs={recs}
        recsLoading={recsLoading}
        recsError={recsError}
        onRecsRetry={() => setRecsRetry((n) => n + 1)}
        role={role}
      />
    </div>
  )
}
