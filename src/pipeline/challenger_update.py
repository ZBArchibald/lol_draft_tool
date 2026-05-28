from src.db.queries import replace_challenger_players
from src.external.riot_api import get_challenger_league_puuids


def update_challenger_players() -> None:
    puuids = get_challenger_league_puuids()
    replace_challenger_players(puuids)
