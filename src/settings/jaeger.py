from typing import Optional

from pydantic import BaseSettings


class JaegerConfig(BaseSettings):
    ENABLED: bool = False
    if ENABLED:
        ENDPOINT: str
    else:
        ENDPOINT: Optional[str]

    class Config:
        env_prefix = 'JAEGER_'
        env_file = '.env'
