from aiopg.sa import Engine
from starlette.requests import Request


async def pg_pool_dep(request: Request) -> Engine:
    return request.app.state.pg_pool
