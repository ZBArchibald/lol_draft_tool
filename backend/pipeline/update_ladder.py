import logging

from backend.db.queries import replace_challenger_players
from backend.external.riot_api import get_challenger_league_puuids

LOG = logging.getLogger(__name__)


def update_ladder() -> None:
    puuids = get_challenger_league_puuids()
    LOG.info("Fetched %d challenger players — updating DB", len(puuids))
    replace_challenger_players(puuids)
    LOG.info("Challenger ladder updated")
