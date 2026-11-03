import type {
  ChampionDict,
  ChampionRecommendation,
  Draft,
  Position,
  SlotRef,
} from '../types'
import TeamColumn from './TeamColumn'
import BanRow from './BanRow'
import ChampionGrid from './ChampionGrid'
import RecommendationsPanel from './RecommendationsPanel'

interface Props {
  champions: ChampionDict
  draft: Draft
  activeSlot: SlotRef | null
  usedChampionIds: Set<number>
  onSlotClick: (slot: SlotRef) => void
  onChampionClick: (championId: number) => void
  recs: ChampionRecommendation[] | null
  recsLoading: boolean
  recsError: string | null
  onRecsRetry: () => void
  role: Position
  onRoleChange: (role: Position) => void
}

// Champion-select shape: your picks | champion grid | enemy picks, with each
// team's bans under its column; recommendations are a bar fixed to the bottom.
// The three columns hold at every width (they shrink, never stack).
export default function DraftBoard({
  champions,
  draft,
  activeSlot,
  usedChampionIds,
  onSlotClick,
  onChampionClick,
  recs,
  recsLoading,
  recsError,
  onRecsRetry,
  role,
  onRoleChange,
}: Props) {
  const draftEmpty =
    draft.bluePicks.every((id) => id === null) && draft.redPicks.every((id) => id === null)

  return (
    <div className="draft-board">
      <TeamColumn
        team="blue"
        picks={draft.bluePicks}
        champions={champions}
        activeSlot={activeSlot}
        onSlotClick={onSlotClick}
      />
      <div className="draft-board-center">
        <ChampionGrid
          champions={champions}
          usedChampionIds={usedChampionIds}
          activeSlot={activeSlot}
          onChampionClick={onChampionClick}
        />
      </div>
      <TeamColumn
        team="red"
        picks={draft.redPicks}
        champions={champions}
        activeSlot={activeSlot}
        onSlotClick={onSlotClick}
      />
      <BanRow
        team="blue"
        bans={draft.blueBans}
        champions={champions}
        activeSlot={activeSlot}
        onSlotClick={onSlotClick}
      />
      <BanRow
        team="red"
        bans={draft.redBans}
        champions={champions}
        activeSlot={activeSlot}
        onSlotClick={onSlotClick}
      />
      <RecommendationsPanel
        recs={recs}
        loading={recsLoading}
        error={recsError}
        champions={champions}
        role={role}
        onRoleChange={onRoleChange}
        draftEmpty={draftEmpty}
        onRetry={onRecsRetry}
      />
    </div>
  )
}
