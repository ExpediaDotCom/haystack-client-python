import logging
from requests import Session
from requests import RequestException
from requests_futures.sessions import FuturesSession
from .recorder import SpanRecorder
from.util import span_to_proto, span_to_json

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 5.0


class ExceptionAwareRequestsSession(Session):
    """This class is needed to prevent exceptions from being swallowed due to the recorder not calling .result() on the
    future."""
    def send(self, request, **kwargs):
        try:
            super().send(request, **kwargs)
        except RequestException as e:
            logging.error(f"Failed to submit span to the http collector due to {e}")


def response_hook(response, *args, **kwargs):
    if response.status_code in range(200, 203):
        logger.debug("successfully submitted the span to http collector")
    else:
        logger.error(f"Failed to submit span to the http collector. Haystack Response: {response}")


class HaystackHttpRecorder(SpanRecorder):
    """Http span recorder which Translates and reports haystack.Spans via threaded executor pool
    at the provided address.
    """

    def __init__(self, collector_url, client_id, api_key, timeout_seconds=DEFAULT_TIMEOUT, use_json_payload=False,
                 executor=None):
        """
        :param collector_url: the haystack collector endpoint
        :param client_id: the haystack client id
        :param api_key: haystack api key provided during registration
        :param timeout_seconds: timeout limit of the requests (these are handled on a background thread)
        :param use_json_payload: set True to enable json payload format.
        :param executor: Can provide a ProcessExecutor pool or ThreadExecutor pool with tuned parameters.
        Default is a ThreadExecutorPool with max 8 threads
        """
        self._collector_url = collector_url
        self._timeout_seconds = timeout_seconds
        self._use_json_payload = use_json_payload
        session = ExceptionAwareRequestsSession()
        session.headers.update({
            "X-Client-Id": client_id,
            "X-Api-Key": api_key,
            "Content-Type": "application/json" if use_json_payload else "application/octet-stream"
        })
        session.hooks["response"] = response_hook
        self._session = FuturesSession(executor=executor, session=session)

    def do_json_request(self, span):
        payload = span_to_json(span)
        logger.debug(f"Haystack Payload = {payload}")
        self._session.post(self._collector_url, json=payload, timeout=self._timeout_seconds)

    def do_binary_request(self, span):
        payload = span_to_proto(span).SerializeToString()
        logger.debug(f"Haystack Payload = {payload}")
        self._session.post(self._collector_url, data=payload, timeout=self._timeout_seconds)

    def record_span(self, span):
        self.do_json_request(span) if self._use_json_payload else self.do_binary_request(span)
