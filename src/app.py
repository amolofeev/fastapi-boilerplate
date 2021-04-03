from fastapi import FastAPI

from .engine import close_engine, create_engine
from .middlewares.metrics import MetricsMiddleware
from .routes import init_routes
from .settings import settings


def get_application() -> FastAPI:
    """Initialize app"""
    application = FastAPI()

    application.add_event_handler('startup', create_engine(application))
    application.add_event_handler('shutdown', close_engine(application))
    init_routes(application)
    application.add_middleware(MetricsMiddleware)

    if settings.jaeger.ENABLED:
        from src.jaeger import init_jaeger
        init_jaeger()

    return application


app = get_application()
