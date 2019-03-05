import logging
from abc import ABC, abstractmethod
from .util import span_to_string

logger = logging.getLogger(__name__)


class SpanRecorder(ABC):
    """A recorder translates and reports finished :class:`Spans`."""

    @abstractmethod
    def record_span(self, span):
        """After the call to finish(), each Span is passed as `span` to
        SpanRecorder.record_span.

        :param BasicSpan span: the finish()'d Span object.
        """
        raise NotImplementedError()


class NoopRecorder(SpanRecorder):
    def record_span(self, span):
        pass


class LoggerRecorder(SpanRecorder):
    def record_span(self, span):
        logger.info(f"SpanRecord = {span_to_string(span)}")
