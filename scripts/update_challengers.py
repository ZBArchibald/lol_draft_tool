from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.challenger_update import update_challenger_players


if __name__ == "__main__":
    update_challenger_players()
