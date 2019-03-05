import opentracing
import time
from threading import Lock


class SpanContext(opentracing.SpanContext):
    """Implements opentracing.SpanContext"""

    def __init__(self,
                 trace_id=None,
                 span_id=None,
                 parent_id=None,
                 baggage=None):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id = parent_id
        self._baggage = baggage or opentracing.SpanContext.EMPTY_BAGGAGE

    @property
    def baggage(self):
        return self._baggage or opentracing.SpanContext.EMPTY_BAGGAGE

    def with_baggage_item(self, key, value):
        baggage = dict(self._baggage)
        if value is not None:
            baggage[key] = value
        else:
            baggage.pop(key, None)
        return SpanContext(trace_id=self.trace_id,
                           span_id=self.span_id,
                           parent_id=self.parent_id,
                           baggage=baggage)


class Span(opentracing.Span):
    """Implements opentracing.Span"""

    def __init__(
            self,
            tracer,
            operation_name=None,
            context=None,
            tags=None,
            start_time=None):
        super().__init__(tracer, context)
        self._tracer = tracer
        self._mutex = Lock()
        self.operation_name = operation_name
        self.start_time = start_time
        self.tags = tags if tags is not None else {}
        self.duration = -1
        self.logs = []

    def set_operation_name(self, operation_name):
        with self._mutex:
            self.operation_name = operation_name
        return self

    def set_tag(self, key, value):
        """Attaches a key/value pair to the :class:`Span`.

        The value must be a string, a bool, or a numeric type.

        If the user calls set_tag multiple times for the same key,
        the behavior of the :class:`Tracer` is undefined, i.e. it is
        implementation specific whether the :class:`Tracer` will retain the
        first value, or the last value, or pick one randomly, or even keep all
        of them.

        :param key: key or name of the tag. Must be a string.
        :type key: str

        :param value: value of the tag.
        :type value: string or bool or int or float

        :rtype: Span
        :return: the :class:`Span` itself, for call chaining.
        """
        with self._mutex:
            if self.tags is None:
                self.tags = {}
            self.tags[key] = value
        return self

    def log_kv(self, key_values, timestamp=None):
        """Adds a log record to the :class:`Span`.

        For example::

            span.log_kv({
                "event": "time to first byte",
                "packet.size": packet.size()})

            span.log_kv({"event": "two minutes ago"}, time.time() - 120)

        :param key_values: A dict of string keys and values of any type
        :type key_values: dict

        :param timestamp: A unix timestamp per :meth:`time.time()`; current
            time if ``None``
        :type timestamp: float

        :rtype: Span
        :return: the :class:`Span` itself, for call chaining.
        """
        with self._mutex:
            self.logs.append(LogData(key_values, timestamp))
        return self

    def finish(self, finish_time=None):
        with self._mutex:
            finish = time.time() if finish_time is None else finish_time
            self.duration = finish - self.start_time
            self._tracer.record(self)

    def set_baggage_item(self, key, value):
        """Stores a Baggage item in the :class:`Span` as a key/value pair.

        Enables powerful distributed context propagation functionality where
        arbitrary application data can be carried along the full path of
        request execution throughout the system.

        Note 1: Baggage is only propagated to the future (recursive) children
        of this :class:`Span`.

        Note 2: Baggage is sent in-band with every subsequent local and remote
        calls, so this feature must be used with care. (Don't create too
        much baggage :)

        Note 3: Baggage is not visible in haystack UI. IPC communication only.

        :param key: Baggage item key
        :type key: str

        :param value: Baggage item value
        :type value: str

        :rtype: Span
        :return: itself, for chaining the calls.
        """
        new_ctx = self.context.with_baggage_item(key=key, value=value)
        with self._mutex:
            self._context = new_ctx
        return self

    def get_baggage_item(self, key):
        with self._mutex:
            return self.context.baggage.get(key)


class LogData(object):
    def __init__(self,
                 key_values,
                 timestamp=None):
        self.key_values = key_values
        self.timestamp = time.time() if timestamp is None else timestamp
