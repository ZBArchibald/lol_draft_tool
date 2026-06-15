from lol_draft_tool.db.queries import replace_challenger_players
from lol_draft_tool.external.riot_api import get_challenger_league_puuids


def update_ladder() -> None:
    puuids = get_challenger_league_puuids()
    replace_challenger_players(puuids)
