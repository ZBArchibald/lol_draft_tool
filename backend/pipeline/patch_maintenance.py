import logging

from backend.core.config import PATCHES_RETAINED
from backend.db.connection import db_connection
from backend.db.queries import (
    delete_data_outside_patches,
    update_metadata,
    upsert_champions,
)
from backend.external.riot_api import champion_table_from_ddragon, get_recent_patches

LOG = logging.getLogger(__name__)

def run_daily_maintenance() -> None:
    prune_old_patches()
    sync_champion_list()

def prune_old_patches() -> None:
    """Keeps the PATCHES_RETAINED newest patches of data and deletes the rest. Runs
    every time (not only on a patch change): it's idempotent and cheap."""
    patches = get_recent_patches(PATCHES_RETAINED)
    update_metadata("current_patch", patches[0])
    LOG.info("Retaining patches: %s", ", ".join(patches))

    with db_connection() as conn:
        delete_data_outside_patches(conn, patches)


def sync_champion_list() -> None:
    champions = champion_table_from_ddragon()
    with db_connection() as conn:
        upsert_champions(conn, champions)
    LOG.info("Synced %d champions", len(champions))
