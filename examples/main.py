import opentracing
import logging
import time
from opentracing import tags
from haystack import HaystackTracer
from haystack import LoggerRecorder


def setup_tracer():
    global recorder
    recorder = LoggerRecorder()

    # instantiate a haystack tracer for this service and set a common tag which applies to all traces
    tracer = HaystackTracer("Service-A",
                            recorder,
                            common_tags={"app.version": "1234"})

    # now set the global tracer, so we can reference it with opentracing.tracer anywhere in our app
    opentracing.set_global_tracer(tracer)


def handle_request(request_body):
    logging.info(f"handling new request - {request_body}")

    # this next line does a few things..  namely, it starts a new scope (which contains the span) to represent
    # the scope of this "work". In this case, it should represent the work involved in processing the entire request
    with opentracing.tracer.start_active_span("a_controller_method") as parent_scope:
        # once within the context of an active span, there are three different ways to assign additional info or
        # or attributes to the span
        """
        First we'll add some tags to the span
        Tags are key:value pairs that enable user-defined annotation of spans in order to query, filter, and 
        comprehend trace data
        Tags have semantic conventions, see https://opentracing.io/specification/conventions/
        *tags do NOT propagate to child spans
        """
        parent_scope.span.set_tag(tags.HTTP_URL, "http://localhost/mocksvc")
        parent_scope.span.set_tag(tags.HTTP_METHOD, "GET")
        parent_scope.span.set_tag(tags.SPAN_KIND, "server")

        """
        Next we'll add some baggage to the span. 
        Baggage carries data across process boundaries.. aka it DOES propagate to child spans
        """
        parent_scope.span.set_baggage_item("business_id", "1234")

        """
        Next lets assume you need to authenticate the client making the request
        """
        with opentracing.tracer.start_active_span("authenticate"):
            time.sleep(.25)  # fake doing some authentication work..

        """
        Finally, we'll add a log event to the request level span.
        Logs are key:value pairs that are useful for capturing timed log messages and other 
        debugging or informational output from the application itself. Logs may be useful for 
        documenting a specific moment or event within the span (in contrast to tags which 
        should apply to the span regardless of time).
        """
        parent_scope.span.log_kv(
            {
                "some_string_value": "foobar",
                "an_int_value": 42,
                "a_float_value": 4.2,
                "a_bool_value": True,
                "an_obj_as_value": {
                    "ok": "hmm",
                    "blah": 4324
                }
            })

        try:
            """
            Now lets say that as part of processing this request, we need to invoke some downstream service
            """
            make_a_downstream_request()
        except Exception:
            # if that fails, we'll tag the request-scoped span with an error so we have success/fail metrics in haystack
            parent_scope.span.set_tag(tags.ERROR, True)


def act_as_remote_service(headers):
    # remote service would have it"s own tracer
    with HaystackTracer("Service-B", recorder) as tracer:
        # simulate network transfer delay
        time.sleep(.25)

        # now as-if this was executing on the remote service, extract the parent span ctx from headers
        upstream_span_ctx = tracer.extract(opentracing.Format.HTTP_HEADERS, headers)
        with tracer.start_active_span("controller_method", child_of=upstream_span_ctx) as parent_scope:
            parent_scope.span.set_tag(tags.SPAN_KIND, "server")
            # simulate downstream service doing some work before replying
            time.sleep(1)


def make_a_downstream_request():
    # create a child span representing the downstream request from current span.
    # Behind the scenes this uses the scope_manger to access the current active
    # span (which would be our request-scoped span called "a_controller_method" and create a child of it.
    with opentracing.tracer.start_active_span("downstream_req") as child_scope:
        child_scope.span.set_tag(tags.SPAN_KIND, "client")

        # In order for the downstream client to use this trace as a parent, we must propagate the current span context.
        # This is done by calling .inject() on the tracer
        headers = {}
        opentracing.tracer.inject(child_scope.span.context, opentracing.Format.HTTP_HEADERS, headers)
        act_as_remote_service(headers)

        # process the response from downstream
        time.sleep(.15)


def main():
    """
    This function represents a "parent" application/service.. i.e. the originating
    service of our traces in this example.

    In this scenario, we're pretending to be a web server.
    """

    # at some point during application init, you'll want to instantiate the global tracer
    setup_tracer()

    # here we assume the web framework invokes this method to handle the given request
    handle_request("hello world")

    # app shutdown
    logging.info("done")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
