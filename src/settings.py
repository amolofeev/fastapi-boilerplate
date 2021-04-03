from pydantic import BaseSettings


class Settings(BaseSettings):
    HOST: str = '0.0.0.0'
    PORT: int = 5000
    DB_DSN: str

    class Config:
        env_file = '.env'


settings = Settings()
