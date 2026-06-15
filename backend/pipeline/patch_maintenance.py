from backend.db.connection import db_connection
from backend.db.queries import (
    clear_all_match_data,
    get_metadata_value,
    update_metadata,
)
from backend.external.riot_api import get_current_patch


def archive_and_clear_on_patch_change() -> None:
    try:
        previous_patch = get_metadata_value("current_patch")
    except KeyError:
        previous_patch = None

    current_patch = update_current_patch()

    if previous_patch and previous_patch != current_patch:
        print(f"Patch changed from {previous_patch} to {current_patch}. Clearing old match data.")
        with db_connection() as conn:
            clear_all_match_data(conn)


def update_current_patch() -> str:
    current_patch = get_current_patch()
    update_metadata("current_patch", current_patch)
    return current_patch
