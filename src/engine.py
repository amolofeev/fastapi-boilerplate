from typing import Awaitable, Callable

import aiopg.sa
from aiopg.sa import Engine
from fastapi import FastAPI

from src.settings import settings


async def init_pg_pool() -> Engine:
    """create engine"""
    return await aiopg.sa.create_engine(
        dsn=settings.PG_DSN,
        timeout=settings.PG_CONNECTION_TIMEOUT,
        minsize=settings.PG_MIN_POOL_SIZE,
        maxsize=settings.PG_MAX_POOL_SIZE

    )


def create_engine(app: FastAPI) -> Callable[[], Awaitable]:
    """decorator"""

    async def __wrap__():
        """store engine in app.state"""
        app.state.pg_pool = await init_pg_pool()

    return __wrap__


def close_engine(app: FastAPI) -> Callable[[], Awaitable]:
    """decorator"""

    async def __wrap__() -> None:
        """close db engine"""
        app.state.pg_pool.close()
        await app.state.pg_pool.wait_closed()

    return __wrap__
