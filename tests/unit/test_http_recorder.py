import unittest
from unittest import mock
from haystack import HaystackHttpRecorder
from haystack.http_recorder import DEFAULT_TIMEOUT


class HttpRecorderTest(unittest.TestCase):

    def setUp(self):
        self.a_url = "http://fake.collector.url"
        self.a_api_key = "any_api_key"
        self.a_client_id = "any_client_id"

    @mock.patch("haystack.http_recorder.span_to_json")
    @mock.patch("haystack.http_recorder.FuturesSession")
    def test_json_payload(self, mock_session, mock_span_to_json):
        test_timeout = 1.0
        recorder = HaystackHttpRecorder(self.a_url, self.a_client_id, self.a_api_key, timeout_seconds=test_timeout,
                                        use_json_payload=True)
        span_as_json = {"fake": "span"}
        mock_span_to_json.return_value = span_as_json

        recorder.record_span(mock.Mock())

        mock_session.return_value.post.assert_called_once_with(self.a_url, json=span_as_json, timeout=test_timeout)

    @mock.patch("haystack.http_recorder.span_to_proto")
    @mock.patch("haystack.http_recorder.FuturesSession")
    def test_timeout_and_payload_defaults(self, mock_session, mock_span_to_proto):
        recorder = HaystackHttpRecorder(self.a_url, self.a_client_id, self.a_api_key)
        proto_string = "a protospan string"
        mock_span_to_proto.return_value.SerializeToString.return_value = proto_string

        recorder.record_span(mock.Mock())

        mock_session.return_value.post.assert_called_once_with(self.a_url, data=proto_string, timeout=DEFAULT_TIMEOUT)
