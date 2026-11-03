import { useMemo, useState } from 'react'
import { POSITIONS, POSITION_LABELS, type ChampionDict, type Position, type SlotRef } from '../types'
import RoleTabs from './RoleTabs'

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
  // Browsing filter only (null = all champions). At most one role is pressed;
  // pressing the active one again releases it. Independent of your recommendation role.
  const [roleFilter, setRoleFilter] = useState<Position | null>(null)

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
  const visible = sorted.filter(
    (c) =>
      (roleFilter === null || c.roles.includes(roleFilter)) &&
      (!query || c.name.toLowerCase().includes(query)),
  )

  return (
    <figure className="mc-window champion-window">
      {/* One toolbar: search + role filter. */}
      <div className="mc-window__bar champion-toolbar">
        <input
          type="search"
          className="champion-search"
          placeholder="Search champions"
          aria-label="Search champions"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <RoleTabs
          label="Filter"
          mode="toggle"
          compact
          hideLabel
          selected={roleFilter}
          onSelect={(position) => setRoleFilter((cur) => (cur === position ? null : position))}
        />
        {/* Same filter as a native dropdown; CSS shows it instead of the buttons in the
            narrow (portrait phone) layout, where five buttons don't fit. */}
        <select
          className="role-select"
          aria-label="Filter champions by role"
          value={roleFilter ?? ''}
          onChange={(e) => setRoleFilter((e.target.value || null) as Position | null)}
        >
          <option value="">All roles</option>
          {POSITIONS.map((position) => (
            <option key={position} value={position}>
              {POSITION_LABELS[position]}
            </option>
          ))}
        </select>
      </div>
      <div className="champion-grid">
        {visible.map((champ) => {
          const used = usedChampionIds.has(champ.id)
          return (
            <button
              key={champ.id}
              className={`champion-cell${used ? ' champion-cell--used' : ''}`}
              onClick={() => onChampionClick(champ.id)}
              disabled={used || activeSlot === null}
              title={champ.name}
            >
              <img src={champ.sprite_url} alt="" loading="lazy" className="champion-cell-icon" />
              <span className="champion-cell-name">{champ.name}</span>
            </button>
          )
        })}
        {visible.length === 0 && (
          <p className="champion-grid-empty">No champions match your filter.</p>
        )}
      </div>
    </figure>
  )
}
