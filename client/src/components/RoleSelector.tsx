import { POSITIONS, type Position } from '../types'

const LABELS: Record<Position, string> = {
  top: 'Top',
  jungle: 'Jungle',
  mid: 'Mid',
  bot: 'Bot',
  support: 'Support',
}

interface Props {
  role: Position
  onChange: (role: Position) => void
}

export default function RoleSelector({ role, onChange }: Props) {
  return (
    <div className="role-selector" role="group" aria-label="Your position">
      <span className="role-selector-label">Your role:</span>
      {POSITIONS.map((position) => (
        <button
          key={position}
          className={`role-button${position === role ? ' role-button--active' : ''}`}
          onClick={() => onChange(position)}
        >
          {LABELS[position]}
        </button>
      ))}
    </div>
  )
}
