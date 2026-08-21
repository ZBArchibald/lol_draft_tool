import type { ChampionInfo } from '../types'

interface Props {
  championInfo: ChampionInfo | null
  isActive: boolean
  onClick: () => void
}

export default function PickSlot({ championInfo, isActive, onClick }: Props) {
  return (
    <button
      className={`pick-slot${isActive ? ' pick-slot--active' : ''}${championInfo ? ' pick-slot--filled' : ''}`}
      onClick={onClick}
      title={championInfo ? `${championInfo.name} (click to clear)` : 'Click to select this slot'}
    >
      {championInfo ? (
        <>
          <img src={championInfo.sprite_url} alt="" className="pick-slot-icon" />
          <span className="pick-slot-name">{championInfo.name}</span>
        </>
      ) : (
        <span className="pick-slot-placeholder">+</span>
      )}
    </button>
  )
}
