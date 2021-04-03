from typing import Awaitable, Callable

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.settings import settings


async def init_pg_pool() -> AsyncEngine:
    """create engine"""
    return create_async_engine(
        url=settings.db.CONNECTION_STRING,
        pool_timeout=settings.db.CONNECTION_TIMEOUT,
        pool_size=settings.db.MIN_POOL_SIZE,
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
        await app.state.pg_pool.dispose()

    return __wrap__
