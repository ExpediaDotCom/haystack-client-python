import opentracing
import logging
import threading
import time
from haystack import HaystackTracer
from haystack import HaystackAgentRecorder

logging.basicConfig(level=logging.DEBUG)

# TODO turn this into a test
if __name__ == "__main__":

    # consumer = KafkaConsumer("proto-spans", api_version=(0, 10), bootstrap_servers="kafkasvc:9092",
    #                          group_id="integration-test",  auto_offset_reset='earliest')

    opentracing.tracer = HaystackTracer("a_tracer", HaystackAgentRecorder("localhost"))

    span = opentracing.tracer.start_span("a-test-span")

    span.finish()


