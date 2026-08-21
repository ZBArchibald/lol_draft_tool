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
}

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
}: Props) {
  const draftEmpty =
    draft.bluePicks.every((id) => id === null) && draft.redPicks.every((id) => id === null)

  // Browsing mode (a slot is active): champion grid in the center, recs in the
  // side column. Idle mode: no champion can be input, so the grid hides and
  // the recommendations take the center instead.
  const browsing = activeSlot !== null

  const recsPanel = (
    <RecommendationsPanel
      recs={recs}
      loading={recsLoading}
      error={recsError}
      champions={champions}
      role={role}
      draftEmpty={draftEmpty}
      onRetry={onRecsRetry}
    />
  )

  return (
    <div className={`draft-board${browsing ? '' : ' draft-board--idle'}`}>
      <TeamColumn
        team="blue"
        picks={draft.bluePicks}
        champions={champions}
        activeSlot={activeSlot}
        onSlotClick={onSlotClick}
      />
      {browsing ? (
        <ChampionGrid
          champions={champions}
          usedChampionIds={usedChampionIds}
          activeSlot={activeSlot}
          onChampionClick={onChampionClick}
        />
      ) : (
        <div className="recs-center">{recsPanel}</div>
      )}
      <TeamColumn
        team="red"
        picks={draft.redPicks}
        champions={champions}
        activeSlot={activeSlot}
        onSlotClick={onSlotClick}
      />
      {browsing && recsPanel}
      <div className="ban-rows">
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
      </div>
    </div>
  )
}
