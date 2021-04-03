# pylint: disable=redefined-outer-name,C0413
import nest_asyncio

nest_asyncio.apply()

import pytest
from aiopg.sa import Engine, SAConnection
from alembic.command import downgrade as alembic_downgrade
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient

from src.app import app
from src.dependencies import pg_pool as pg_pool_dependency
from src.engine import init_pg_pool


@pytest.fixture
async def pg_engine(loop):  # pylint: disable=unused-argument
    """fixture for migrations"""
    engine = await init_pg_pool()

    config = AlembicConfig('alembic.ini')
    alembic_upgrade(config, 'head')

    yield engine

    alembic_downgrade(config, 'base')

    engine.close()
    await engine.wait_closed()


@pytest.fixture
async def db_connection(pg_engine: Engine) -> SAConnection:
    """fixture for connection"""
    async with pg_engine.acquire() as conn:
        yield conn


@pytest.fixture
async def application(pg_engine):  # pylint: disable=W0613
    """override dependencies"""
    app.dependency_overrides[pg_pool_dependency] = lambda: pg_engine

    yield app

    app.dependency_overrides = {}


@pytest.fixture
async def client(application):
    """Test http client"""
    yield TestClient(application)
