import { POSITIONS, POSITION_LABELS, POSITION_SHORT_LABELS, type Position } from '../types'

interface Props {
  label: string // control label, e.g. "Filter" / "Your role" (always the accessible name)
  hideLabel?: boolean // keep the label for screen readers only
  selected: Position | null
  onSelect: (position: Position) => void
  // 'radio': exactly one is always selected (your role).
  // 'toggle': at most one is pressed; the caller releases it on a repeat click (grid filter).
  mode: 'radio' | 'toggle'
  compact?: boolean // always use the short labels (JG / SUP), e.g. in a crowded toolbar
}

// Shared row of role buttons used by the champion-grid filter and the
// recommendations role selector, so both look and size (incl. touch) the same.
export default function RoleTabs({ label, selected, onSelect, mode, compact = false, hideLabel = false }: Props) {
  return (
    <div className={`role-tabs${compact ? ' role-tabs--compact' : ''}`}>
      {!hideLabel && <span className="control-label">{label}</span>}
      <div className="mc-tabs" role={mode === 'radio' ? 'radiogroup' : 'group'} aria-label={label}>
        {POSITIONS.map((position) => {
          const on = position === selected
          return (
            <button
              key={position}
              className="mc-tab"
              {...(mode === 'radio'
                ? { role: 'radio', 'aria-checked': on, 'aria-selected': on }
                : { 'aria-pressed': on })}
              aria-label={POSITION_LABELS[position]}
              onClick={() => onSelect(position)}
            >
              <span className="tab-label-long">{POSITION_LABELS[position]}</span>
              <span className="tab-label-short" aria-hidden="true">
                {POSITION_SHORT_LABELS[position]}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
