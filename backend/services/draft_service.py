from backend.domain.draft_state import DraftState
from backend.db.queries import get_candidate_champions, get_champion_relationships, get_winrate

def recommend_champions(draft_state: DraftState) -> dict:
    # find all candidate champions to suggest to user
        # champions with at least 5% pickrate in role will be considered.
    
    excluded = set(draft_state.banned + draft_state.allies + draft_state.enemies)
    candidate_champions = [
        c for c in get_candidate_champions(draft_state.position.value, minimum_rolerate=.05)
        if c not in excluded
    ]
    
    # for each considerable champion, average their relationship winrate against each of the other champions that have been drafted in draft_state
        # place these all in a dictionary key=champ value=wrscore
            #sort by wr score and return to user

    candidate_champion_winchances = {}
    for candidate_champion in candidate_champions:
        candidate_champion_winchances[candidate_champion] = _predict_win_chance(candidate_champion, draft_state)

    reccomendations = dict(
        sorted(candidate_champion_winchances.items(), key=lambda x: x[1], reverse=True)
    )
    return reccomendations

def _predict_win_chance(champion: str, draft_state: DraftState) -> float:
    drafted_champions = draft_state.allies + draft_state.enemies
    if not drafted_champions:
        return get_winrate(champion)

    relationships = get_champion_relationships(champion, drafted_champions)

    relationship_win_rates = []
    for ally in draft_state.allies:
        rel = relationships.get(ally)
        if rel and rel["games_as_ally"] > 0:
            relationship_win_rates.append(rel["wins_as_ally"] / rel["games_as_ally"])

    for enemy in draft_state.enemies:
        rel = relationships.get(enemy)
        if rel and rel["games_as_opponent"] > 0:
            relationship_win_rates.append(rel["wins_as_opponent"] / rel["games_as_opponent"])

    if not relationship_win_rates:
        return get_winrate(champion)

    return sum(relationship_win_rates) / len(relationship_win_rates)