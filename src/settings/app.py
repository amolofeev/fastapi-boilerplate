from pydantic import BaseSettings


class AppConfig(BaseSettings):
    ENVIRONMENT: str = 'localhost'
    NAME: str = 'web'

    class Config:
        env_prefix = 'APP_'
        env_file = '.env'
