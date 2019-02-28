import opentracing
import logging
import unittest
from kafka import KafkaConsumer
import threading
import time
from haystack.span_pb2 import Span
from haystack import HaystackTracer
from haystack import HaystackAgentRecorder
from haystack import AsyncHttpRecorder

logging.basicConfig(level=logging.INFO)
consumer = KafkaConsumer("proto-spans", bootstrap_servers="kafkasvc:9092")


def send_a_span(span_name):
    time.sleep(1.0)  # give kafka consumer a second to connect
    span = opentracing.tracer.start_span(span_name)
    span.set_tag("span.kind", "server")
    client_span = opentracing.tracer.start_span(f"{span_name}-client", child_of=span.context)
    client_span.set_tag("span.kind", "client")
    client_span.finish()
    span.finish()


def get_spans():
    spans = {}
    for i in range(2):
        print("waiting for next record")
        msg = next(consumer)
        print(f"found span = {msg}")
        span = Span()
        span.ParseFromString(msg.value)
        if span.tags.pop().vStr == "client":
            spans["client"] = span
        else:
            spans["server"] = span
    return spans


class HaystackIntegrationTests(unittest.TestCase):
    """
    Note: If running in IDE, need to provide 'localhost' hostname to both recorders
    """

    def test_haystack_agent(self):
        span_name = "agent-test-span"
        service_name = "agent-test"

        opentracing.tracer = HaystackTracer(service_name, HaystackAgentRecorder("sandbox_haystack_agent_1"))
        thread = threading.Thread(target=send_a_span, args=(span_name,))

        thread.start()
        retrieved_spans = get_spans()

        client_span = retrieved_spans["client"]
        server_span = retrieved_spans["server"]

        self.assertEqual(f"{span_name}-client", client_span.operationName)
        self.assertEqual(span_name, server_span.operationName)

        self.assertEqual(service_name, server_span.serviceName)
        self.assertEqual(service_name, client_span.serviceName)

        self.assertEqual(client_span.parentSpanId, server_span.spanId)
        self.assertEqual(client_span.traceId, server_span.traceId)

    def test_http_collector(self):
        span_name = "http-test-span"
        service_name = "http-test"

        opentracing.tracer = HaystackTracer(service_name,
                                            AsyncHttpRecorder(
                                                collector_url="http://sandbox_haystack_collector_1:8080/span"))
        thread = threading.Thread(target=send_a_span, args=(span_name,))

        thread.start()
        retrieved_spans = get_spans()

        client_span = retrieved_spans["client"]
        server_span = retrieved_spans["server"]

        self.assertEqual(f"{span_name}-client", client_span.operationName)
        self.assertEqual(span_name, server_span.operationName)

        self.assertEqual(service_name, server_span.serviceName)
        self.assertEqual(service_name, client_span.serviceName)

        self.assertEqual(client_span.parentSpanId, server_span.spanId)
        self.assertEqual(client_span.traceId, server_span.traceId)


if __name__ == "__main__":
    unittest.main()












