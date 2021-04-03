from aiopg.sa import Engine, SAConnection
from fastapi import Depends
from starlette.requests import Request


async def pg_pool(request: Request) -> Engine:
    return request.app.state.pg_pool


async def pg_connection(pool: Engine = Depends(pg_pool)) -> SAConnection:
    async with pool.acquire() as connection:
        yield connection
