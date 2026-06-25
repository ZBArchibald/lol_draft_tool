from backend.core.logging_config import setup_logging
from backend.pipeline.patch_maintenance import archive_and_clear_on_patch_change


def main() -> None:
    setup_logging()
    archive_and_clear_on_patch_change()


if __name__ == "__main__":
    main()
