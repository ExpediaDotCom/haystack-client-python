import logging
import json
from requests import Session
from requests import RequestException
from requests_futures.sessions import FuturesSession
from .recorder import SpanRecorder
from .util import span_to_proto, span_to_json
from .constants import DEFAULT_HTTP_TIMEOUT

logger = logging.getLogger(__name__)


def response_hook(response, *args, **kwargs):
    if response.status_code in range(200, 203):
        logger.debug("successfully submitted the span to http collector")
    else:
        logger.error(f"Failed to submit span to the http collector. "
                     f"Haystack Response: {response}")


class SyncHttpRecorder(SpanRecorder):
    """Http span recorder which Translates and reports haystack.Spans
    in-process."""

    def __init__(self,
                 collector_url="http://haystack-collector:8080/span",
                 headers={},
                 timeout_seconds=DEFAULT_HTTP_TIMEOUT,
                 use_json_payload=False,
                 requests_session=None):
        """
        :param collector_url: the haystack collector endpoint
        :param timeout_seconds: timeout limit of the requests
        :param use_json_payload: set True to enable json payload format.
        """
        self._collector_url = collector_url
        self._timeout_seconds = timeout_seconds
        self._use_json_payload = use_json_payload
        self._session = requests_session or Session()
        headers["Content-Type"] = "application/json" if use_json_payload \
            else "application/octet-stream"
        self._session.headers.update(headers)
        self._session.hooks["response"] = response_hook

    @staticmethod
    def get_json_payload(span):
        json_span = span_to_json(span)
        str_span = json.dumps(
            json_span,
            default=lambda o: f"{o.__class__.__name__} is not serializable"
        )
        return str_span.encode("utf-8")

    @staticmethod
    def get_binary_payload(span):
        proto_span = span_to_proto(span)
        return proto_span.SerializeToString()

    def post_payload(self, payload):
        try:
            logger.debug(f"Haystack Payload = {payload}")
            self._session.post(self._collector_url,
                               data=payload,
                               timeout=self._timeout_seconds)
        except RequestException as e:
            logger.error(f"Failed to submit span to the http collector due "
                         f"to {e}")

    def record_span(self, span):
        try:
            payload = self.get_json_payload(span) if self._use_json_payload \
                else self.get_binary_payload(span)
        except TypeError:
            logger.exception("failed to convert span")
        self.post_payload(payload)


class ExceptionHandlingRequestsSession(Session):
    """This class is needed to prevent exceptions from being swallowed due to
    the async recorder not calling .result()
    on the future."""
    def send(self, request, **kwargs):
        try:
            super().send(request, **kwargs)
        except RequestException as e:
            logger.error(f"Failed to submit span to the http collector due "
                         f"to {e}")


class AsyncHttpRecorder(SyncHttpRecorder):
    """Http span recorder which Translates and reports haystack.Spans via
    threaded executor pool.
    """

    def __init__(self,
                 collector_url="http://haystack-collector:8080/span",
                 headers={},
                 timeout_seconds=DEFAULT_HTTP_TIMEOUT,
                 use_json_payload=False,
                 executor=None):
        """
        :param collector_url: the haystack collector endpoint
        :param timeout_seconds: timeout limit of the requests (these are
         handled on a background thread)
        :param use_json_payload: set True to enable json payload format.
        :param executor: Can provide a ProcessExecutor pool or ThreadExecutor
         pool with tuned parameters.
        Default is a ThreadExecutorPool with max 8 threads
        """
        super().__init__(collector_url=collector_url,
                         headers=headers,
                         timeout_seconds=timeout_seconds,
                         use_json_payload=use_json_payload,
                         requests_session=ExceptionHandlingRequestsSession())

        self._session = FuturesSession(executor=executor,
                                       session=self._session)
