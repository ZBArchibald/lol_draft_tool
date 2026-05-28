from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.match_sync import sync_all_challenger_matches


if __name__ == "__main__":
    sync_all_challenger_matches()
