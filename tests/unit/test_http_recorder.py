import unittest
import json
from unittest import mock
from haystack import AsyncHttpRecorder
from haystack import SyncHttpRecorder
from haystack.http_recorder import DEFAULT_TIMEOUT


class AsyncHttpRecorderTest(unittest.TestCase):

    def setUp(self):
        self.a_url = "http://fake.collector.url"

    @mock.patch("haystack.http_recorder.span_to_json")
    @mock.patch("haystack.http_recorder.FuturesSession")
    def test_async_recorder_with_json_payload_and_custom_timeout(self, mock_futures_session, mock_span_to_json):
        test_timeout = 1.0
        recorder = AsyncHttpRecorder(self.a_url, timeout_seconds=test_timeout, use_json_payload=True)
        span_as_json = {"fake": "span"}
        mock_span_to_json.return_value = span_as_json

        recorder.record_span(mock.Mock())

        expected_payload = json.dumps(span_as_json).encode("utf-8")
        mock_futures_session.return_value.post.assert_called_once_with(self.a_url, data=expected_payload,
                                                                       timeout=test_timeout)

    @mock.patch("haystack.http_recorder.span_to_proto")
    @mock.patch("haystack.http_recorder.FuturesSession")
    def test_async_recorder_defaults_to_proto_with_default_timeout(self, mock_futures_session, mock_span_to_proto):
        recorder = AsyncHttpRecorder(self.a_url, )
        proto_string = "a protospan string"
        mock_span_to_proto.return_value.SerializeToString.return_value = proto_string

        recorder.record_span(mock.Mock())

        mock_futures_session.return_value.post.assert_called_once_with(self.a_url, data=proto_string,
                                                                       timeout=DEFAULT_TIMEOUT)


class SyncHttpRecorderTest(unittest.TestCase):

    def setUp(self):
        self.a_url = "http://fake.collector.url"

    @mock.patch("haystack.http_recorder.span_to_json")
    @mock.patch("haystack.http_recorder.Session")
    def test_sync_recorder_with_json_payload_and_custom_timeout(self, mock_session, mock_span_to_json):
        test_timeout = 1.0
        recorder = SyncHttpRecorder(self.a_url, timeout_seconds=test_timeout, use_json_payload=True)
        span_as_json = {"fake": "span"}
        mock_span_to_json.return_value = span_as_json

        recorder.record_span(mock.Mock())

        expected_payload = json.dumps(span_as_json).encode("utf-8")
        mock_session.return_value.post.assert_called_once_with(self.a_url, data=expected_payload, timeout=test_timeout)

    @mock.patch("haystack.http_recorder.span_to_proto")
    @mock.patch("haystack.http_recorder.Session")
    def test_sync_recorder_defaults_to_proto_with_default_timeout(self, mock_session, mock_span_to_proto):
        recorder = SyncHttpRecorder(self.a_url, )
        proto_string = "a protospan string"
        mock_span_to_proto.return_value.SerializeToString.return_value = proto_string

        recorder.record_span(mock.Mock())

        mock_session.return_value.post.assert_called_once_with(self.a_url, data=proto_string, timeout=DEFAULT_TIMEOUT)


if __name__ == "__main__":
    unittest.main()
