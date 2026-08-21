import type { ChampionInfo } from '../types'

interface Props {
  championInfo: ChampionInfo | null
  isActive: boolean
  onClick: () => void
}

export default function BanSlot({ championInfo, isActive, onClick }: Props) {
  return (
    <button
      className={`ban-slot${isActive ? ' ban-slot--active' : ''}${championInfo ? ' ban-slot--filled' : ''}`}
      onClick={onClick}
      title={championInfo ? `Banned: ${championInfo.name} (click to clear)` : 'Click to select this ban slot'}
    >
      {championInfo ? (
        <img src={championInfo.sprite_url} alt={championInfo.name} className="ban-slot-icon" />
      ) : (
        <span className="ban-slot-placeholder">✕</span>
      )}
    </button>
  )
}
