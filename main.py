import uvicorn

from src.app import app
from src.settings import settings

uvicorn.run(app, host=settings.HOST, port=settings.PORT)
