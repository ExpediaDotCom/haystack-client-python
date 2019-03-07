from .propagator import Propagator
from .span import SpanContext
from opentracing import SpanContextCorruptedException
from .constants import (
    SPAN_ID_HEADERS,
    TRACE_ID_HEADER,
    PARENT_SPAN_ID_HEADERS,
    BAGGAGE_HEADER_PREFIX,
)


class TextPropagator(Propagator):
    """A propagator for Format.TEXT_MAP and Format.HTTP_HEADERS"""

    def inject(self, span_context, carrier):
        carrier[TRACE_ID_HEADER] = span_context.trace_id
        carrier[SPAN_ID_HEADERS[0]] = span_context.span_id
        carrier[PARENT_SPAN_ID_HEADERS[0]] = span_context.parent_id
        if span_context.baggage is not None:
            for item in span_context.baggage:
                carrier[BAGGAGE_HEADER_PREFIX + item] = \
                    span_context.baggage[item]

    def extract(self, carrier):
        count = 0
        baggage = {}
        parent_id = None

        for key in carrier:
            value = carrier[key]
            if key in SPAN_ID_HEADERS:
                span_id = value
                count += 1
            elif key == TRACE_ID_HEADER:
                trace_id = value
                count += 1
            elif key.startswith(BAGGAGE_HEADER_PREFIX):
                baggage[key[len(BAGGAGE_HEADER_PREFIX):]] = value
            elif key in PARENT_SPAN_ID_HEADERS:
                parent_id = value

        if count == 0:
            return None
        elif count != 2:
            raise SpanContextCorruptedException(
                "Both SpanID and TraceID are required")

        return SpanContext(span_id=span_id,
                           trace_id=trace_id,
                           parent_id=parent_id,
                           baggage=baggage)
