import unittest
from opentracing import SpanContextCorruptedException
from haystack.text_propagator import TextPropagator


class TextPropagatorTest(unittest.TestCase):

    def setUp(self):
        self.propagator = TextPropagator()

    def test_message_id_in_carrier_should_be_extracted_as_span_id(self):
        span_id = "1234"
        parent_id = "4321"
        trace_id = "1212"
        carrier = {"Message-ID": span_id, "Parent-Message-ID": parent_id,
                   "Trace-ID": trace_id}

        ctx = self.propagator.extract(carrier)

        self.assertEqual(ctx.span_id, span_id)
        self.assertEqual(ctx.parent_id, parent_id)
        self.assertEqual(ctx.trace_id, trace_id)

    def test_corrupted_context_throws_exception(self):
        span_id = "1234"
        carrier = {"Message-ID": span_id, "Span-ID": "123456",
                   "Trace-ID": "1234567"}  # two span id's are invalid

        self.assertRaises(SpanContextCorruptedException, self.propagator.extract, carrier)

    def test_no_context_in_carrier_returns_none(self):
        span_id = "1234"
        carrier = {"Not-A-Message-ID": span_id, "Not-A-Trace-ID": "123456"}

        ctx = self.propagator.extract(carrier)

        self.assertIsNone(ctx)


if __name__ == "__main__":
    unittest.main()
