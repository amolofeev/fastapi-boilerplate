import time
import traceback
from contextlib import contextmanager
from contextvars import ContextVar
from logging import getLogger
from typing import Dict, List, Optional, Union

from opentelemetry.exporter.jaeger.thrift.gen.jaeger.ttypes import Batch
from opentelemetry.exporter.jaeger.thrift.gen.jaeger.ttypes import Process as OPTLProcess
from opentelemetry.exporter.jaeger.thrift.gen.jaeger.ttypes import Span as OPTLSpan
from opentelemetry.exporter.jaeger.thrift.gen.jaeger.ttypes import (
    SpanRef,
    SpanRefType,
    Tag,
    TagType,
)
from opentelemetry.exporter.jaeger.thrift.send import Collector
from opentelemetry.exporter.jaeger.thrift.translate import (
    _convert_int_to_i64,
    _get_trace_id_high,
    _get_trace_id_low,
    _nsec_to_usec_round,
)
from opentelemetry.sdk.trace import RandomIdGenerator

from .settings import settings


logger = getLogger(__name__)


class TagMixin:
    tags: Optional[List[Tag]]

    def tag(self: Union[OPTLSpan, OPTLProcess], key: str, value):
        typed_value: dict
        if isinstance(value, bool):
            typed_value = {'vType': TagType.BOOL, 'vBool': value}
        elif isinstance(value, str):
            typed_value = {'vType': TagType.STRING, 'vStr': value}
        elif isinstance(value, int):
            typed_value = {'vType': TagType.LONG, 'vLong': value}
        elif isinstance(value, float):
            typed_value = {'vType': TagType.DOUBLE, 'vDouble': value}
        else:  # vBinary
            typed_value = {'vType': TagType.STRING, 'vStr': str(value)}
        if self.tags is None:
            self.tags = []
        self.tags.append(
            Tag(key=key, **typed_value),
        )


class Span(TagMixin, OPTLSpan):
    ...  # noqa: WPS604


class Process(TagMixin, OPTLProcess):
    ...  # noqa: WPS604


CurrentSpan: ContextVar[Span] = ContextVar('CurrentSpan')
CurrentProcess: ContextVar[Process] = ContextVar('CurrentProcess')
CurrentCollector: ContextVar[Collector] = ContextVar('Collector')
RootTraceID: ContextVar[int] = ContextVar('RootTraceID')
RootSpanID: ContextVar[int] = ContextVar('RootSpanID')


def create_remote_span(tid, sid):
    trace_id = int(tid, 0)
    span_id = int(sid, 0)
    span = Span(
        traceIdLow=_get_trace_id_low(trace_id),
        traceIdHigh=_get_trace_id_high(trace_id),
        spanId=_convert_int_to_i64(span_id),
    )
    RootTraceID.set(trace_id)
    RootSpanID.set(span_id)
    return span


def create_span(operation: str, parent: Optional[Span] = None):
    trace_id = RandomIdGenerator().generate_trace_id()
    span_id = RandomIdGenerator().generate_span_id()
    if parent is None:
        RootTraceID.set(trace_id)
        RootSpanID.set(span_id)
    span = Span(
        traceIdLow=_get_trace_id_low(trace_id) if parent is None else parent.traceIdLow,
        traceIdHigh=_get_trace_id_high(trace_id) if parent is None else parent.traceIdHigh,
        spanId=_convert_int_to_i64(span_id),
        parentSpanId=0,
        operationName=operation,
        references=None if parent is None else [
            SpanRef(
                SpanRefType.CHILD_OF,
                parent.traceIdLow,
                parent.traceIdLow,
                parent.spanId,
            ),
        ],
        flags=1,
        startTime=time.time_ns(),
        duration=None,
        tags=None,
        logs=None,
    )
    return span


@contextmanager
def start_span(operation: str):
    if (current_span := CurrentSpan.get(None)) is not None:
        span = create_span(operation, current_span)
    else:
        span = create_span(operation)
    token = CurrentSpan.set(span)

    tags: Dict = {'error': False}
    try:
        yield span
    except BaseException as e:
        try:   # noqa: WPS505
            stacktrace = traceback.format_exc()
        except:  # noqa: E722, B001
            stacktrace = 'Exception occurred on stacktrace formatting'
        tags = {
            'error': True,
            'exception.type': e.__class__.__name__,
            'exception.message': str(e),
            'exception.stacktrace': stacktrace,
            'exception.escaped': str(False),
        }

        raise
    finally:
        span.duration = _nsec_to_usec_round(time.time_ns() - span.startTime)
        span.startTime = _nsec_to_usec_round(span.startTime)

        for key, value in tags.items():
            span.tag(key, value)

        collector = CurrentCollector.get(None)
        if collector is not None:
            batch = Batch(CurrentProcess.get(None), [span])
            try:  # noqa: WPS505
                collector.submit(batch)
            except BaseException as e:
                logger.warning(f'unable submit batch: {e}')
    CurrentSpan.reset(token)


def init_jaeger(name: Optional[str] = None):

    process = Process()
    process.tag('service.env', settings.app.ENVIRONMENT)
    process.serviceName = name or settings.app.NAME
    CurrentProcess.set(process)

    CurrentCollector.set(
        Collector(settings.jaeger.ENDPOINT),
    )
