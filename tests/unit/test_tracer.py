import unittest
from haystack import HaystackTracer
from haystack.recorder import NoopRecorder
from haystack.span import SpanContext


class HaystackTracerTests(unittest.TestCase):
    """
    Tests haystack specific tracer features.
    Most of tracer testing is handled in api compatibility checks from opentracing
    """

    def test_common_tags_are_applied_to_new_spans(self):
        common_tags = {"a": "common_tag", "another": "common_tag"}
        tracer = HaystackTracer("any_service", NoopRecorder(),
                                common_tags=common_tags)

        span = tracer.start_span("any_operation")

        self.assertDictEqual(common_tags, span.tags)

    def test_common_tags_are_overridden_if_span_specifies_the_same(self):
        common_tags = {"a": "common_tag", "another": "common_tag"}
        tracer = HaystackTracer("any_service", NoopRecorder(),
                                common_tags=common_tags)

        span_tags = {"another": "span_tag"}
        span = tracer.start_span("any_operation", tags=span_tags)

        expected_tags = {**common_tags, **span_tags}
        self.assertDictEqual(expected_tags, span.tags)

    def test_non_shared_spans_are_created_by_default(self):
        tracer = HaystackTracer("any_service", NoopRecorder())
        trace_id = "123"
        span_id = "1234"
        parent_id = "12345"
        upstream_ctx = SpanContext(trace_id=trace_id, span_id=span_id,
                                   parent_id=parent_id)

        span = tracer.start_span("any_operation", child_of=upstream_ctx)

        self.assertEqual(span.context.trace_id, trace_id)
        self.assertNotEqual(span.context.span_id, span_id)
        self.assertEqual(span.context.parent_id, span_id)

    def test_shared_spans_are_created_when_enabled(self):
        tracer = HaystackTracer("any_service", NoopRecorder(),
                                use_shared_spans=True)
        trace_id = "123"
        span_id = "1234"
        parent_id = "12345"
        upstream_ctx = SpanContext(trace_id=trace_id, span_id=span_id,
                                   parent_id=parent_id)

        span = tracer.start_span("any_operation", child_of=upstream_ctx)

        self.assertEqual(span.context.trace_id, trace_id)
        self.assertEqual(span.context.span_id, span_id)
        self.assertEqual(span.context.parent_id, parent_id)

    def test_b3_format_ids_are_used_when_enabled(self):
        tracer = HaystackTracer("any_service", NoopRecorder, use_b3_ids=True)
        span = tracer.start_span("any_operation")

        self.assertTrue("-" not in span.context.trace_id)
        self.assertTrue(len(span.context.trace_id) == 32)
        self.assertTrue("-" not in span.context.span_id)
        self.assertTrue(len(span.context.span_id) == 32)

    def test_b3_format_ids_are_not_used_when_disabled(self):
        tracer = HaystackTracer("any_service", NoopRecorder, use_b3_ids=False)
        span = tracer.start_span("any_operation")

        self.assertTrue("-" in span.context.trace_id)
        self.assertTrue("-" in span.context.span_id)


if __name__ == "__main__":
    unittest.main()
