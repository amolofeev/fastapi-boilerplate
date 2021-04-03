from pydantic import BaseSettings


class DBConfig(BaseSettings):
    # PostgreSQL
    CONNECTION_STRING: str
    CONNECTION_TIMEOUT: int = 20
    MIN_POOL_SIZE: int = 1
    MAX_POOL_SIZE: int = 5

    class Config:
        env_prefix = 'DB_'
        env_file = '.env'
