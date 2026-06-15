from backend.db.queries import replace_challenger_players
from backend.external.riot_api import get_challenger_league_puuids


def update_ladder() -> None:
    puuids = get_challenger_league_puuids()
    replace_challenger_players(puuids)
