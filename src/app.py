from fastapi import FastAPI

from .engine import close_engine, create_engine
from .routes import init_routes


def get_application() -> FastAPI:
    """Initialize app"""
    application = FastAPI()

    application.add_event_handler('startup', create_engine(application))
    application.add_event_handler('shutdown', close_engine(application))
    init_routes(application)

    return application


app = get_application()
