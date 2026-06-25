from backend.core.logging_config import setup_logging
from backend.db.schema import initialize_database


def main() -> None:
    setup_logging()
    initialize_database()


if __name__ == "__main__":
    main()
