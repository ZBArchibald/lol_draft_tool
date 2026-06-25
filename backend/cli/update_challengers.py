from backend.core.logging_config import setup_logging
from backend.pipeline.update_ladder import update_ladder


def main() -> None:
    setup_logging()
    update_ladder()


if __name__ == "__main__":
    main()
