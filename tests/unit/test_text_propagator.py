import unittest
from opentracing import SpanContextCorruptedException
from haystack.text_propagator import TextPropagator
from haystack.propagator import PropagatorOpts
from haystack.constants import (
    TRACE_ID,
    SPAN_ID,
    PARENT_SPAN_ID,
    BAGGAGE_PREFIX,
)


class TextPropagatorTest(unittest.TestCase):

    def setUp(self):
        self.propagator = TextPropagator()

    def test_span_id_without_trace_id_throws_exception(self):
        carrier = {"Span-ID": "123456", "Foo-ID": "1234567"}

        self.assertRaises(SpanContextCorruptedException,
                          self.propagator.extract, carrier)

    def test_trace_id_without_span_id_throws_exception(self):
        carrier = {"Trace-ID": "123456", "Foo-ID": "1234567"}

        self.assertRaises(SpanContextCorruptedException,
                          self.propagator.extract, carrier)

    def test_no_context_in_carrier_returns_none(self):
        span_id = "1234"
        carrier = {"Not-A-Message-ID": span_id, "Not-A-Trace-ID": "123456"}

        ctx = self.propagator.extract(carrier)

        self.assertIsNone(ctx)

    def test_lowercase_headers_are_still_extracted(self):
        pass

    def test_default_propagator_options_injected_and_context_is_extracted(self):
        span_id = "1234"
        parent_id = "4321"
        trace_id = "1212"
        baggage = {"Item1": "Value1", "Item2": "Value2"}
        carrier = {TRACE_ID: trace_id, SPAN_ID: span_id, PARENT_SPAN_ID: parent_id}
        for key, value in baggage.items():
            carrier[BAGGAGE_PREFIX + key] = value

        ctx = self.propagator.extract(carrier)

        self.assertEqual(ctx.span_id, span_id)
        self.assertEqual(ctx.parent_id, parent_id)
        self.assertEqual(ctx.trace_id, trace_id)
        self.assertDictEqual(ctx.baggage, baggage)

    def test_custom_propagator_options_are_injected_and_context_is_extracted(self):
        propagator = TextPropagator(PropagatorOpts("X-Trace-ID", "X-Span-ID",
                                                   "X-Parent-ID", "X-baggage-"))
        span_id = "1234"
        parent_id = "4321"
        trace_id = "1212"
        carrier = {"X-Span-ID": span_id, "X-Parent-ID": parent_id,
                   "X-Trace-ID": trace_id}
        baggage = {"Item1": "Value1", "Item2": "Value2"}
        for key, value in baggage.items():
            carrier["X-baggage-" + key] = value

        ctx = propagator.extract(carrier)

        self.assertEqual(ctx.span_id, span_id)
        self.assertEqual(ctx.parent_id, parent_id)
        self.assertEqual(ctx.trace_id, trace_id)


if __name__ == "__main__":
    unittest.main()
