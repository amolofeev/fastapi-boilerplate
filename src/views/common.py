from aiopg.sa import SAConnection
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response

from src.dependencies import pg_connection

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
        conn: SAConnection = Depends(pg_connection),
) -> HealthCheckResponse:
    coroutines = {
        'postgres': conn.scalar('select True;')
    }
    service_status = {}
    for service, coroutine in coroutines.items():
        try:
            await coroutine
        except: # noqa
            service_status[service] = False
        else:
            service_status[service] = True
    status_code = 200
    if not all(service_status.values()):
        status_code = 500
    response.status_code = status_code
    return HealthCheckResponse(**service_status)
