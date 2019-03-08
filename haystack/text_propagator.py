from .propagator import Propagator, PropagatorOpts
from .span import SpanContext
from opentracing import SpanContextCorruptedException


class TextPropagator(Propagator):
    """A propagator for Format.TEXT_MAP and Format.HTTP_HEADERS"""

    def __init__(self, propagator_opts=None):
        """
        Initialize with optional custom keys for the carrier.
        :param propagator_opts: PropagatorOps named tuple with custom keys
        to inject and extract :class:SpanContext from the carrier.
        """
        self._propagator_opts = propagator_opts or PropagatorOpts()

    def inject(self, span_context, carrier):
        carrier[self._propagator_opts.trace_id_key] = span_context.trace_id
        carrier[self._propagator_opts.span_id_key] = span_context.span_id
        carrier[self._propagator_opts.parent_id_key] = span_context.parent_id
        if span_context.baggage is not None:
            for item in span_context.baggage:
                carrier[self._propagator_opts.baggage_key_prefix + item] = \
                    span_context.baggage[item]

    def extract(self, carrier):
        count = 0
        baggage = {}
        parent_id = None

        for key in carrier:
            lc_key = key.lower()
            value = carrier[key]
            if lc_key == self._propagator_opts.span_id_key.lower():
                span_id = value
                count += 1
            elif lc_key == self._propagator_opts.trace_id_key.lower():
                trace_id = value
                count += 1
            elif lc_key.startswith(
                    self._propagator_opts.baggage_key_prefix.lower()):
                baggage[
                    key[len(self._propagator_opts.baggage_key_prefix):]] = \
                    value
            elif lc_key == self._propagator_opts.parent_id_key.lower():
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
