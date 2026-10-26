import logging

from backend.db.queries import replace_ladder_players
from backend.external.riot_api import (
    get_challenger_league_puuids,
    get_grandmaster_league_puuids,
)

LOG = logging.getLogger(__name__)


def update_ladder() -> None:
    challenger_puuids = get_challenger_league_puuids()
    grandmaster_puuids = get_grandmaster_league_puuids()
    LOG.info(
        "Fetched %d challenger and %d grandmaster players — updating DB",
        len(challenger_puuids),
        len(grandmaster_puuids),
    )
    # replace_ladder_players deletes anyone not in the list it's given, so both tiers
    # must go in a single call; a player in both lists keeps the Challenger tier
    players = {puuid: "GRANDMASTER" for puuid in grandmaster_puuids}
    players.update({puuid: "CHALLENGER" for puuid in challenger_puuids})
    replace_ladder_players(list(players.items()))
    LOG.info("Ladder updated (%d players)", len(players))
