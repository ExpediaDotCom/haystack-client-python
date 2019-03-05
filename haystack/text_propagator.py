from .propagator import Propagator
from .span import SpanContext
from opentracing import SpanContextCorruptedException
from .constants import (
    SPAN_ID_HEADER,
    TRACE_ID_HEADER,
    PARENT_SPAN_ID_HEADER,
    BAGGAGE_HEADER_PREFIX,
    ALTERNATE_SPAN_ID_HEADERS,
)


class TextPropagator(Propagator):
    """A propagator for Format.TEXT_MAP and Format.HTTP_HEADERS"""

    def inject(self, span_context, carrier):
        carrier[TRACE_ID_HEADER] = span_context.trace_id
        carrier[SPAN_ID_HEADER] = span_context.span_id
        carrier[PARENT_SPAN_ID_HEADER] = span_context.parent_id
        if span_context.baggage is not None:
            for item in span_context.baggage:
                carrier[BAGGAGE_HEADER_PREFIX + item] = \
                    span_context.baggage[item]

    def extract(self, carrier):
        count = 0
        baggage = {}

        for key in carrier:
            value = carrier[key]
            if key == SPAN_ID_HEADER:
                span_id = value
                count += 1
            elif key == TRACE_ID_HEADER:
                trace_id = value
                count += 1
            elif key.startswith(BAGGAGE_HEADER_PREFIX):
                baggage[key[len(BAGGAGE_HEADER_PREFIX):]] = value
            elif key in ALTERNATE_SPAN_ID_HEADERS:
                span_id = value
                count += 1

        if count == 0:
            return None
        elif count != 2:
            raise SpanContextCorruptedException()

        return SpanContext(span_id=span_id, trace_id=trace_id, baggage=baggage)
