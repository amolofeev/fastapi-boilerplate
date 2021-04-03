from typing import Optional

from prometheus_client import Counter, Summary
from pydantic import BaseSettings


class PodInfo(BaseSettings):
    name: Optional[str]
    ip: Optional[str]
    node: Optional[str]
    namespace: Optional[str]
    image: Optional[str]
    version: Optional[str]

    class Config:
        env_prefix = 'POD_'
        env_file = '.env'


pod: PodInfo = PodInfo()


class LogConfig(BaseSettings):
    LEVEL: str = 'INFO'
    FORMATTER: Optional[str] = 'json'
    pod: PodInfo = pod

    EXTRA: dict = {
        **{f'pod.{k}': v for k, v in pod.dict().items()}
    }

    class Config:
        env_prefix = 'LOG_'
        env_file = '.env'


class Metrics:
    requests_count = Counter(
        'requests_count', 'rps',
        ['url', 'method', 'status_code']
    )
    requests_latency = Summary(
        'requests_latency', 'request latency',
        ['url', 'method', 'status_code']
    )
