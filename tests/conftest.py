# pylint: disable=redefined-outer-name,C0413
import pytest
from alembic.command import downgrade as alembic_downgrade
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from src.app import app
from src.dependencies import pg_pool_dep
from src.engine import init_pg_pool


@pytest.fixture
async def pg_engine(event_loop):  # pylint: disable=unused-argument
    """fixture for migrations"""
    engine = await init_pg_pool()

    config = AlembicConfig('alembic.ini')
    alembic_upgrade(config, 'head')

    yield engine

    alembic_downgrade(config, 'base')

    await engine.dispose()


@pytest.fixture
async def db_connection(pg_engine: AsyncEngine):
    """fixture for connection"""
    async with pg_engine.begin() as conn:
        yield conn


@pytest.fixture
async def application(pg_engine):  # pylint: disable=W0613
    """override dependencies"""
    app.dependency_overrides[pg_pool_dep] = lambda: pg_engine

    yield app

    app.dependency_overrides = {}


@pytest.fixture
async def client(application):
    """Test http client"""
    yield TestClient(application)
