from .propagator import Propagator
from .span import SpanContext
from opentracing import SpanContextCorruptedException

TRACE_ID = "Trace-ID"
SPAN_IDS = ["Span-ID", "Message-ID"]
PARENT_SPAN_ID = "Parent-ID"
BAGGAGE_PREFIX = "Baggage-"


class TextPropagator(Propagator):
    """A propagator for Format.TEXT_MAP and Format.HTTP_HEADERS"""

    def inject(self, span_context, carrier):
        carrier[TRACE_ID] = span_context.trace_id
        carrier[SPAN_IDS[0]] = span_context.span_id
        carrier[PARENT_SPAN_ID] = span_context.parent_id
        if span_context.baggage is not None:
            for item in span_context.baggage:
                carrier[BAGGAGE_PREFIX + item] = span_context.baggage[item]

    def extract(self, carrier):
        count = 0
        baggage = {}
        for key in carrier:
            value = carrier[key]
            if key in SPAN_IDS:
                span_id = value
                count += 1
            elif key == TRACE_ID:
                trace_id = value
                count += 1
            elif key.startswith(BAGGAGE_PREFIX):
                baggage[key[len(BAGGAGE_PREFIX):]] = value

        if count == 0:
            return None
        elif count != 2:
            raise SpanContextCorruptedException()

        return SpanContext(span_id=span_id, trace_id=trace_id, baggage=baggage)
