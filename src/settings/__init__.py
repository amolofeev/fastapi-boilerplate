import logging.config
import sys
from typing import Optional

import ujson
from pydantic import BaseSettings

from .app import AppConfig
from .db import DBConfig
from .jaeger import JaegerConfig
from .log import LogConfig, Metrics


class Settings(BaseSettings):
    app: AppConfig = AppConfig()
    db: DBConfig = DBConfig()
    log: LogConfig = LogConfig()
    metrics: Metrics = Metrics()
    jaeger: JaegerConfig = JaegerConfig()


settings = Settings()


class JSONFormatter(logging.Formatter):
    def __init__(self, *args, params: Optional[dict] = None, extra: Optional[dict]=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._params = params.copy() if params else {}
        self._extra = extra.copy() if extra else {}

    def format(self, record: logging.LogRecord) -> str:
        result = {
            'time': record.created,
            'name': record.name,
            'level': record.levelname,
            'msg': record.getMessage(),
            'func': f'{record.module}.{record.funcName}:{record.lineno}',
        }

        if record.exc_info:
            exc_info = self.formatException(record.exc_info)
            result['exc_info'] = exc_info
        result.update(self._extra)

        return ujson.dumps(result, **self._params)


CONFIG_DICT: dict = dict(
    version=1,
    disable_existing_loggers=False,
    loggers={
        '': {
            'level': settings.log.LEVEL,
            'handlers': ['console'],
        },
        'uvicorn': {
            'level': settings.log.LEVEL,
            'handlers': ['console'],
        },
        'root': {
            'level': settings.log.LEVEL,
            'handlers': ['console'],
            'propagate': False,
        }
    },
    handlers={
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': settings.log.FORMATTER,
            'stream': sys.stdout,
        }
    },
    formatters={
        'json': {
            '()': JSONFormatter,
            'params': {
                'ensure_ascii': False
            },
            'extra': settings.log.EXTRA
        },
    },
)

logging.config.dictConfig(CONFIG_DICT)
