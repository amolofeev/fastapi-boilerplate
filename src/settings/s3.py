from typing import Optional

from pydantic import BaseSettings


class S3Config(BaseSettings):
    ENABLED: bool = False
    if ENABLED:
        ACCESS_KEY_ID: str
        SECRET_ACCESS_KEY: str
        ENDPOINT_URL: str
    else:
        ACCESS_KEY_ID: Optional[str]
        SECRET_ACCESS_KEY: Optional[str]
        ENDPOINT_URL: Optional[str]
    LIVENESS_URL: str = f'{ENDPOINT_URL}/minio/health/cluster'

    class Config:
        env_prefix = 'S3_'
        env_file = '.env'
