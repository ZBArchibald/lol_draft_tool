import { useMemo, useState } from 'react'
import type { ChampionDict, SlotRef } from '../types'

interface Props {
  champions: ChampionDict
  usedChampionIds: Set<number>
  activeSlot: SlotRef | null
  onChampionClick: (championId: number) => void
}

export default function ChampionGrid({
  champions,
  usedChampionIds,
  activeSlot,
  onChampionClick,
}: Props) {
  const [search, setSearch] = useState('')

  // App creates a fresh SlotRef object per activation, so a reference change
  // here means a slot was just clicked — reset the search for the new slot.
  const [prevSlot, setPrevSlot] = useState(activeSlot)
  if (activeSlot !== prevSlot) {
    setPrevSlot(activeSlot)
    if (activeSlot !== null) setSearch('')
  }

  const sorted = useMemo(
    () =>
      Object.entries(champions)
        .map(([id, info]) => ({ id: Number(id), ...info }))
        .sort((a, b) => a.name.localeCompare(b.name)),
    [champions],
  )

  const query = search.trim().toLowerCase()
  const visible = query
    ? sorted.filter((c) => c.name.toLowerCase().includes(query))
    : sorted

  return (
    <div className="champion-grid-panel">
      <div className="champion-grid-toolbar">
        <input
          type="search"
          className="champion-search"
          placeholder="Search champions…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <span className="champion-grid-hint">Pick a champion for the selected slot</span>
      </div>
      <div className="champion-grid">
        {visible.map((champ) => {
          const used = usedChampionIds.has(champ.id)
          return (
            <button
              key={champ.id}
              className={`champion-cell${used ? ' champion-cell--used' : ''}`}
              onClick={() => onChampionClick(champ.id)}
              disabled={used}
              title={champ.name}
            >
              <img src={champ.sprite_url} alt="" loading="lazy" className="champion-cell-icon" />
              <span className="champion-cell-name">{champ.name}</span>
            </button>
          )
        })}
        {visible.length === 0 && (
          <p className="champion-grid-empty">No champions match “{search}”</p>
        )}
      </div>
    </div>
  )
}
