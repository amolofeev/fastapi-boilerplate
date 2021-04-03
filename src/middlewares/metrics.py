from fastapi import Request
from prometheus_client.context_managers import Timer
from starlette.middleware.base import BaseHTTPMiddleware

from src.settings import settings


class TimerCallback:
    time: float

    def set_result(self, time):
        self.time = time


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        timer = TimerCallback()
        with Timer(timer, 'set_result'):
            response = await call_next(request)
            labels = dict(
                url=request.scope["path"],
                method=request.method,
                status_code=response.status_code
            )

        settings.metrics.requests_count.labels(**labels).inc(1)
        settings.metrics.requests_latency.labels(**labels).observe(timer.time)
        return response
