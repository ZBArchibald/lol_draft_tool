from backend.core.logging_config import setup_logging
from backend.pipeline.ingest_and_process_matches import sync_all_challenger_matches


def main() -> None:
    setup_logging()
    sync_all_challenger_matches()


if __name__ == "__main__":
    main()
