import { useEffect, useState, type FocusEvent, type MouseEvent } from 'react'
import {
  POSITION_LABELS,
  type ChampionDict,
  type ChampionRecommendation,
  type Position,
} from '../types'
import RoleTabs from './RoleTabs'

// Name label anchored above one item, in viewport coordinates.
interface Label {
  champion: number
  left: number
  top: number
}

interface Props {
  recs: ChampionRecommendation[] | null
  loading: boolean
  error: string | null
  champions: ChampionDict
  role: Position
  onRoleChange: (role: Position) => void
  draftEmpty: boolean
  onRetry: () => void
}

// Bar fixed to the bottom of the viewport: heading (left) + your-role selector (right),
// then every returned champion left to right, sized so 15 fill the width (scroll for the
// rest), score bar under each icon, then the score note. Hovering/focusing an icon shows its name; clicking
// pins the name (for touch); pressing anywhere outside the icons clears the pin.
export default function RecommendationsPanel({
  recs,
  loading,
  error,
  champions,
  role,
  onRoleChange,
  draftEmpty,
  onRetry,
}: Props) {
  const rows = (recs ?? [])
    .filter((rec) => champions[rec.champion] !== undefined)

  // Two sources: `hovered` follows the pointer/focus; `pinned` is set by a click.
  // Hover wins, so pointing at another icon shows its name even while one is pinned.
  const [hovered, setHovered] = useState<Label | null>(null)
  const [pinned, setPinned] = useState<Label | null>(null)

  // Read currentTarget synchronously: React nulls it once the handler returns.
  const anchor = (champion: number, el: HTMLElement): Label => {
    const rect = el.getBoundingClientRect()
    return { champion, left: rect.left + rect.width / 2, top: rect.top - 6 }
  }
  const show = (champion: number) => (e: MouseEvent<HTMLElement> | FocusEvent<HTMLElement>) =>
    setHovered(anchor(champion, e.currentTarget))
  const hide = () => setHovered(null)
  const toggle = (champion: number) => (e: MouseEvent<HTMLElement>) => {
    const next = anchor(champion, e.currentTarget)
    setPinned((cur) => (cur?.champion === champion ? null : next))
  }
  const clearAll = () => {
    setHovered(null)
    setPinned(null)
  }

  // Any press outside the recommendation icons clears the pinned name.
  useEffect(() => {
    if (!pinned) return
    const onPointerDown = (e: PointerEvent) => {
      if (!(e.target instanceof Element) || !e.target.closest('.recs-item')) setPinned(null)
    }
    document.addEventListener('pointerdown', onPointerDown)
    return () => document.removeEventListener('pointerdown', onPointerDown)
  }, [pinned])

  const label = hovered ?? pinned
  // A label for a champion that dropped out of the list would float orphaned.
  const labelInfo =
    label && rows.some((r) => r.champion === label.champion) ? champions[label.champion] : null

  return (
    <aside className="recs-panel">
      <div className="recs-controls">
        <div className="recs-header">
          <h2 className="mc-heading">RECOMMENDATIONS</h2>
          {loading && <span className="mc-status">LOADING</span>}
        </div>
        <RoleTabs label="Your role" mode="radio" selected={role} onSelect={onRoleChange} />
      </div>
      {error ? (
        <div className="recs-error">
          <span>{error}</span>
          <button className="mc-btn" onClick={onRetry}>
            RETRY
          </button>
        </div>
      ) : rows.length === 0 && !loading ? (
        <p className="recs-empty">No recommendations yet for this role.</p>
      ) : (
        <ol
          className={`recs-list${loading ? ' recs-list--stale' : ''}`}
          onScroll={clearAll}
        >
          {rows.map((rec, i) => {
            const info = champions[rec.champion]
            const score = rec.win_chance * 100
            return (
              <li key={rec.champion}>
                <button
                  className="recs-item"
                  aria-label={`#${i + 1} ${info.name}, score ${score.toFixed(1)}`}
                  aria-pressed={pinned?.champion === rec.champion}
                  onMouseEnter={show(rec.champion)}
                  onMouseLeave={hide}
                  onFocus={show(rec.champion)}
                  onBlur={hide}
                  onClick={toggle(rec.champion)}
                >
                  <img src={info.sprite_url} alt="" className="recs-item-icon" />
                  <span className="recs-item-bar">
                    <span className="recs-item-bar-fill" style={{ width: `${score}%` }} />
                  </span>
                  <span className="recs-item-score">{score.toFixed(1)}</span>
                </button>
              </li>
            )
          })}
        </ol>
      )}
      {/* The note sits under the portraits, where the scores it explains are. */}
      <p className="recs-subtitle">
        {draftEmpty ? (
          <>
            <b>Score</b> = each champion's {POSITION_LABELS[role]} win rate this patch. Picks
            will refine it.
          </>
        ) : (
          <>
            <b>Score</b> = average win rate with each of your allies and against each enemy
            picked so far. A ranking, not a win probability.
          </>
        )}
      </p>
      {label && labelInfo && (
        <span className="recs-tooltip" style={{ left: label.left, top: label.top }} role="tooltip">
          {labelInfo.name}
        </span>
      )}
    </aside>
  )
}
