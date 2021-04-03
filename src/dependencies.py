from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.requests import Request


async def pg_pool_dep(request: Request) -> AsyncEngine:
    return request.app.state.pg_pool
