from backend.db.queries import (
    get_candidate_champions,
    get_champion_relationships_bulk,
    get_winrates,
)
from backend.domain.draft_state import DraftState


def recommend_champions(draft_state: DraftState) -> dict:
    # find all candidate champions to suggest to user
        # champions with at least 20% pickrate in role will be considered.

    excluded = set(draft_state.banned + draft_state.allies + draft_state.enemies)
    candidate_champions = [
        c for c in get_candidate_champions(draft_state.position.value, minimum_rolerate=.2)
        if c not in excluded
    ]

    drafted_champions = draft_state.allies + draft_state.enemies
    winrates = get_winrates(candidate_champions)
    relationships = get_champion_relationships_bulk(candidate_champions, drafted_champions)

    candidate_champion_winchances = {
        candidate_champion: _predict_win_chance_naive(candidate_champion, draft_state, winrates, relationships)
        for candidate_champion in candidate_champions
    }

    reccomendations = dict(
        sorted(candidate_champion_winchances.items(), key=lambda x: x[1], reverse=True)
    )
    return reccomendations

def _predict_win_chance_naive(
    champ_id: int,
    draft_state: DraftState,
    winrates: dict[int, float],
    relationships: dict[int, dict[int, dict]],
) -> float:
    baseline_winrate = winrates.get(champ_id, 0.5)

    drafted_champions = draft_state.allies + draft_state.enemies
    if not drafted_champions:
        return baseline_winrate

    champion_relationships = relationships.get(champ_id, {})

    relationship_win_rates = []
    for ally in draft_state.allies:
        rel = champion_relationships.get(ally)
        if rel and rel["games_as_ally"] > 0:
            relationship_win_rates.append(rel["wins_as_ally"] / rel["games_as_ally"])

    for enemy in draft_state.enemies:
        rel = champion_relationships.get(enemy)
        if rel and rel["games_as_opponent"] > 0:
            relationship_win_rates.append(rel["wins_as_opponent"] / rel["games_as_opponent"])

    if not relationship_win_rates:
        return baseline_winrate

    return sum(relationship_win_rates) / len(relationship_win_rates)