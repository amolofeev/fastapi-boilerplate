from aiopg.sa import SAConnection
from fastapi import APIRouter, Depends

from src.dependencies import pg_connection

router = APIRouter()


@router.get('/liveness', response_model=dict, tags=['common'])
async def liveness_handler(
        conn: SAConnection = Depends(pg_connection)
) -> dict:
    await conn.scalar('select True;')
    return dict(ok=True)


@router.get('/readiness', response_model=dict, tags=['common'])
async def readiness_handler(
        conn: SAConnection = Depends(pg_connection)
) -> dict:
    await conn.scalar('select True;')
    return dict(ok=True)
