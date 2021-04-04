from pydantic import BaseSettings


class Settings(BaseSettings):
    # app TCP listener
    HOST: str = '0.0.0.0'
    PORT: int = 5000

    # PostgreSQL
    PG_DSN: str
    PG_CONNECTION_TIMEOUT: int = 20
    PG_MIN_POOL_SIZE: int = 1
    PG_MAX_POOL_SIZE: int = 5

    class Config:
        env_file = '.env'


settings = Settings()
