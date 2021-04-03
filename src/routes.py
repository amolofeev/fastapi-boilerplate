from fastapi import FastAPI

from .views import common


def init_routes(application: FastAPI):
    application.include_router(common.router)
