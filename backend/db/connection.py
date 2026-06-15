import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from backend.core.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
