import type { ChampionDict, SlotRef, Team } from '../types'
import PickSlot from './PickSlot'

interface Props {
  team: Team
  picks: (number | null)[]
  champions: ChampionDict
  activeSlot: SlotRef | null
  onSlotClick: (slot: SlotRef) => void
}

export default function TeamColumn({ team, picks, champions, activeSlot, onSlotClick }: Props) {
  return (
    <div className={`team-column team-column--${team}`}>
      <h2 className="team-column-title">
        {team === 'blue' ? 'Your team' : 'Enemy team'}
      </h2>
      {picks.map((championId, index) => {
        const slot: SlotRef = { team, kind: 'pick', index }
        const isActive =
          activeSlot?.team === team &&
          activeSlot.kind === 'pick' &&
          activeSlot.index === index
        return (
          <PickSlot
            key={index}
            championInfo={championId !== null ? champions[championId] : null}
            isActive={isActive}
            onClick={() => onSlotClick(slot)}
          />
        )
      })}
    </div>
  )
}
