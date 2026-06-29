from backend.domain.draft_state import DraftState
from backend.db.queries import get_candidate_champions

def recommend_champions(draft_state: DraftState) -> dict:
    # find all candidate champions to suggest to user
        # champions with at least 5% pickrate in role will be considered.
    
    candidate_champions = get_candidate_champions(draft_state.position, minimum_rolerate=.05)
    
    # for each considerable champion, average their relationship winrate against each of the other champions that have been drafted in draft_state
        # place these all in a dictionary key=champ value=wrscore
            #sort by wr score and return to user

    candidate_champion_winchances = {}
    for candidate_champion in candidate_champions:
        candidate_champion_winchances[candidate_champion] = _predict_win_chance(candidate_champion, draft_state)

    recommendation_hierarchy = dict(
        sorted(candidate_champion_winchances.items(), key=lambda x: x[1], reverse=True)
    )
    return recommendation_hierarchy

def _predict_win_chance(champion: str, draft_state: DraftState) -> float: 
    return