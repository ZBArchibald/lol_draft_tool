import logging

from backend.db.connection import db_connection
from backend.db.queries import (
    clear_player_data,
    get_metadata_value,
    update_metadata,
    upsert_champions,
)
from backend.external.riot_api import get_champion_list, get_current_patch

LOG = logging.getLogger(__name__)


def archive_and_clear_on_patch_change() -> None:
    try:
        previous_patch = get_metadata_value("current_patch")
    except KeyError:
        previous_patch = None

    current_patch = update_current_patch()
    LOG.info("Current patch: %s", current_patch)

    if previous_patch and previous_patch != current_patch:
        LOG.info("Patch changed from %s to %s — clearing old match data", previous_patch, current_patch)
        with db_connection() as conn:
            clear_player_data(conn)
    else:
        LOG.info("No patch change detected")

    sync_champion_list()


def update_current_patch() -> str:
    current_patch = get_current_patch()
    update_metadata("current_patch", current_patch)
    return current_patch


def sync_champion_list() -> None:
    champions = get_champion_list()
    with db_connection() as conn:
        upsert_champions(conn, champions)
    LOG.info("Synced %d champions", len(champions))
