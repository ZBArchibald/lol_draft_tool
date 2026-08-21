import type { ChampionDict, ChampionRecommendation, Position } from '../types'

const TOP_N = 10

interface Props {
  recs: ChampionRecommendation[] | null
  loading: boolean
  error: string | null
  champions: ChampionDict
  role: Position
  draftEmpty: boolean
  onRetry: () => void
}

export default function RecommendationsPanel({
  recs,
  loading,
  error,
  champions,
  role,
  draftEmpty,
  onRetry,
}: Props) {
  const rows = (recs ?? [])
    .filter((rec) => champions[rec.champion] !== undefined)
    .slice(0, TOP_N)

  return (
    <aside className="recs-panel">
      <div className="recs-header">
        <h2>Recommendations</h2>
        {loading && <span className="recs-spinner" aria-label="Updating" />}
      </div>
      <p className="recs-subtitle">
        {draftEmpty ? `Baseline ranking for ${role} (no picks yet)` : `Best ${role} picks for this draft`}
      </p>
      {error ? (
        <div className="recs-error">
          <p className="error-text">{error}</p>
          <button onClick={onRetry}>Retry</button>
        </div>
      ) : (
        <ol className={`recs-list${loading ? ' recs-list--stale' : ''}`}>
          {rows.map((rec) => {
            const info = champions[rec.champion]
            const score = rec.win_chance * 100
            return (
              <li key={rec.champion} className="recs-row">
                <img src={info.sprite_url} alt="" className="recs-row-icon" />
                <span className="recs-row-name">{info.name}</span>
                <span className="recs-row-score">{score.toFixed(1)}</span>
                <span className="recs-row-bar">
                  <span className="recs-row-bar-fill" style={{ width: `${score}%` }} />
                </span>
              </li>
            )
          })}
        </ol>
      )}
      <p className="recs-footnote">
        Scores are relative rankings from ally/enemy matchup winrates, not calibrated win
        probabilities.
      </p>
    </aside>
  )
}
