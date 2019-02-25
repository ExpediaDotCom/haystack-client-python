import unittest
import opentracing
from haystack import HaystackTracer
from haystack.recorder import NoopRecorder


class HaystackTracerTests(unittest.TestCase):
    """
    Tests haystack specific tracer features.
    Most of tracer testing is handled in api compatibility checks from opentracing
    """

    def test_common_tags_are_applied_to_new_spans(self):
        common_tags = {"a": "common_tag", "another": "common_tag"}
        tracer = HaystackTracer("any_service", NoopRecorder(), common_tags=common_tags)

        span = tracer.start_span("any_operation")

        self.assertDictEqual(common_tags, span.tags)

    def test_common_tags_are_overridden_if_span_specifies_the_same(self):
        common_tags = {"a": "common_tag", "another": "common_tag"}
        tracer = HaystackTracer("any_service", NoopRecorder(), common_tags=common_tags)

        span_tags = {"another": "span_tag"}
        span = tracer.start_span("any_operation", tags=span_tags)

        expected_tags = {**common_tags, **span_tags}
        self.assertDictEqual(expected_tags, span.tags)
