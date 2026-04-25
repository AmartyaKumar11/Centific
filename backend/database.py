import ssl

import asyncpg

from config import DATABASE_URL

pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global pool
    if pool is None:
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not configured")
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        pool = await asyncpg.create_pool(
            DATABASE_URL,
            ssl=ssl_context,
            min_size=2,
            max_size=10,
        )
    return pool


async def close_pool() -> None:
    global pool
    if pool:
        await pool.close()
        pool = None
