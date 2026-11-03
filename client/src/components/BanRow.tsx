import type { ChampionDict, SlotRef, Team } from '../types'
import BanSlot from './BanSlot'

interface Props {
  team: Team
  bans: (number | null)[]
  champions: ChampionDict
  activeSlot: SlotRef | null
  onSlotClick: (slot: SlotRef) => void
}

export default function BanRow({ team, bans, champions, activeSlot, onSlotClick }: Props) {
  return (
    <div className={`ban-row ban-row--${team}`}>
      <h2 className="mc-heading ban-row-label">{team === 'blue' ? 'YOUR BANS' : 'ENEMY BANS'}</h2>
      <div className="ban-row-slots">
        {bans.map((championId, index) => {
          const slot: SlotRef = { team, kind: 'ban', index }
          const isActive =
            activeSlot?.team === team &&
            activeSlot.kind === 'ban' &&
            activeSlot.index === index
          return (
            <BanSlot
              key={index}
              championInfo={championId !== null ? champions[championId] : null}
              isActive={isActive}
              onClick={() => onSlotClick(slot)}
            />
          )
        })}
      </div>
    </div>
  )
}
