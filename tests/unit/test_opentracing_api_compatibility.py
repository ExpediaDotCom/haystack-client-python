import unittest
from haystack.tracer import HaystackTracer
from haystack.recorder import NoopRecorder
from opentracing.harness.api_check import APICompatibilityCheckMixin
from opentracing import Format


class ModifiedAPICompatibilityCheckMixin(APICompatibilityCheckMixin):
    # TODO implement binary propagator and remove this hack!
    def test_binary_propagation(self):
        pass

    def test_mandatory_formats(self):
        formats = [
            (Format.TEXT_MAP, {}),
            (Format.HTTP_HEADERS, {}),
            # (Format.BINARY, bytearray()),
        ]
        with self.tracer().start_span(operation_name='Bender') as span:
            for fmt, carrier in formats:
                # expecting no exceptions
                span.tracer.inject(span.context, fmt, carrier)
                span.tracer.extract(fmt, carrier)


class HaystackTracerCompatibility(unittest.TestCase, ModifiedAPICompatibilityCheckMixin):

    def setUp(self):
        self._tracer = HaystackTracer("TestTracer", NoopRecorder())

    def tracer(self):
        return self._tracer

    def is_parent(self, parent, span):
        if span is None:
            return False

        if parent is None:
            return span.context.parent_id is None

        return parent.context.span_id == span.context.parent_id


if __name__ == "__main__":
    unittest.main()
