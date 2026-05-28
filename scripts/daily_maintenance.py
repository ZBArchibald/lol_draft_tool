from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.patch_maintenance import archive_and_clear_on_patch_change


if __name__ == "__main__":
    archive_and_clear_on_patch_change()
