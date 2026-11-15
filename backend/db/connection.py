import atexit
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg_pool import ConnectionPool

from backend.core.config import DATABASE_URL

_pool: ConnectionPool | None = None


def _get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        if not DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL is not set. Add it to the .env file in the project root, "
                "e.g. DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require"
            )
        # check_connection pings each connection before handing it out, so a connection
        # Neon dropped while idle (scale-to-zero, restart) is replaced instead of
        # failing the request that happens to get it
        _pool = ConnectionPool(
            DATABASE_URL,
            min_size=1,
            max_size=4,
            check=ConnectionPool.check_connection,
        )
        atexit.register(_pool.close)
    return _pool


@contextmanager
def db_connection() -> Iterator[psycopg.Connection]:
    pool = _get_pool()
    with pool.connection() as conn:
        yield conn
