import opentracing
import time
import logging
from opentracing.ext import tags
from haystack import HaystackTracer
from haystack import AsyncHttpRecorder
from haystack import LoggerRecorder

recorder = LoggerRecorder()
logging.basicConfig(level=logging.DEBUG)


def act_as_remote_service(headers):
    # remote service would have it"s own tracer
    with HaystackTracer("Service-B", recorder,) as tracer:
        opentracing.tracer = tracer

        # simulate network transfer delay
        time.sleep(.25)

        # now as-if this was executing on the remote service, extract the parent span ctx from headers
        upstream_span_ctx = opentracing.tracer.extract(opentracing.Format.HTTP_HEADERS, headers)
        with opentracing.tracer.start_active_span("controller_method", child_of=upstream_span_ctx) as parent_scope:
            parent_scope.span.set_tag(tags.SPAN_KIND, "server")
            # simulate downstream service doing some work before replying
            time.sleep(1)


def make_a_downstream_request():
    # create a child span representing the downstream request from current span.
    # Behind the scenes this uses the scope_manger to access the current active
    # span and create a child of it.
    with opentracing.tracer.start_active_span("downstream_req") as child_scope:

        child_scope.span.set_tag(tags.SPAN_KIND, "client")

        # add some baggage (i.e. something that should propagate across
        # process boundaries)
        child_scope.span.set_baggage_item("baggage-item", "baggage-item-value")

        # carrier here represents http headers
        carrier = {}
        opentracing.tracer.inject(child_scope.span.context, opentracing.Format.HTTP_HEADERS, carrier)
        act_as_remote_service(carrier)

        # process the response from downstream
        time.sleep(.15)


def use_http_recorder():
    endpoint = "http://<replace_me>"
    global recorder
    recorder = AsyncHttpRecorder(collector_url=endpoint)


def main():
    """
    Represents an application/service
    """
    # instantiate a tracer with app version common tag and set it
    # to opentracing.tracer property
    opentracing.tracer = HaystackTracer("Service-A",
                                        recorder,
                                        common_tags={"app.version": "1234"})

    logging.info("mock request received")
    with opentracing.tracer.start_active_span("a_controller_method") as parent_scope:

        # add a tag, tags are part of a span and do not propagate
        # (tags have semantic conventions, see https://opentracing.io/specification/conventions/)
        parent_scope.span.set_tag(tags.HTTP_URL, "http://localhost/mocksvc")
        parent_scope.span.set_tag(tags.HTTP_METHOD, "GET")
        parent_scope.span.set_tag(tags.SPAN_KIND, "server")

        # doing some work.. validation, processing, etc
        time.sleep(.25)

        # tag the span with some information about the processing
        parent_scope.span.log_kv(
            {"string": "foobar", "int": 42, "float": 4.2, "bool": True, "obj": {"ok": "hmm", "blah": 4324}})

        make_a_downstream_request()

        # uncomment this line to tag the span with an error
        # parent_scope.span.set_tag(tags.ERROR, True)

    logging.info("done in main")


if __name__ == "__main__":
    # uncomment line below to send traces to haystack collector using http recorder
    # use_http_recorder()
    main()
