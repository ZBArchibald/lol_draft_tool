from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.db.connection import db_connection
from src.db.queries import get_metadata_value, update_metadata
from src.external.riot_api import get_current_patch


def archive_and_clear_on_patch_change() -> None:
    try:
        previous_patch = get_metadata_value("current_patch")
    except KeyError:
        # No previous patch recorded, just set the current one
        previous_patch = None
    
    current_patch = get_current_patch()
    
    if previous_patch and previous_patch != current_patch:
        print(f"Patch changed from {previous_patch} to {current_patch}. Clearing old match data.")
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM processed_matches")
            cursor.execute("DELETE FROM champion_relationships")
            cursor.execute("DELETE FROM challenger_players")
    
    update_metadata("current_patch", current_patch)


if __name__ == "__main__":
    archive_and_clear_on_patch_change()
