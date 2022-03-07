import logging

from aiopg.sa import Engine
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import Response

from src.dependencies import pg_pool_dep

logger = logging.getLogger(__file__)
router = APIRouter()


class HealthCheckResponse(BaseModel):
    postgres: bool


@router.get('/liveness',
            response_model=HealthCheckResponse,
            responses={500: {'model': HealthCheckResponse}},
            tags=['common'])
@router.get('/readiness',
            response_model=HealthCheckResponse,
            responses={500: {'model': HealthCheckResponse}},
            tags=['common'])
async def liveness_handler(
        response: Response,
        pg_engine: Engine = Depends(pg_pool_dep),
) -> HealthCheckResponse:
    coroutines = {
        'postgres': check_postgres(pg_engine)
    }
    service_status = {}
    for service, coroutine in coroutines.items():
        try:
            await coroutine
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(e)
            service_status[service] = False
        else:
            service_status[service] = True
    status_code = 200
    if not all(service_status.values()):
        status_code = 500
    response.status_code = status_code
    return HealthCheckResponse(**service_status)


async def check_postgres(pg_pool: Engine) -> None:
    async with pg_pool.acquire() as conn:
        await conn.scalar('select True;')
