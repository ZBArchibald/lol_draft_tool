import sys

from backend.core.logging_config import setup_logging

from backend.db.schema import initialize_database
from backend.pipeline.ingest_and_process_matches import sync_all_challenger_matches
from backend.pipeline.patch_maintenance import run_daily_maintenance
from backend.pipeline.update_ladder import update_ladder

USAGE = "usage: ldt {init-db,daily-maintenance,update-challengers,run-match-sync}"


def main() -> None:
    args = sys.argv[1:]
    if not args:
        # sys.exit with a string prints it to stderr and exits with status 1
        sys.exit(USAGE)

    setup_logging()

    match args[0]:
        case "init-db":
            initialize_database()

        case "daily-maintenance":
            run_daily_maintenance()

        case "update-challengers":
            update_ladder()

        case "run-match-sync":
            sync_all_challenger_matches()

        case _:
            # without this, a typo'd command would exit 0 having done nothing,
            # which shows up as a green-but-empty GitHub Actions run
            sys.exit(f"ldt: unknown command '{args[0]}'\n{USAGE}")

    return
