# AWS Lambda Example
import opentracing
import os
from requests import RequestException
from opentracing.ext import tags
from haystack import HaystackTracer
from haystack import SyncHttpRecorder

"""
Note: Recorder implementation in serverless applications requires careful 
consideration. For Example, in AWS, due to the way AWS lambda freezes execution 
context, it's not reliable to send requests via the AsyncHttpRecorder. If the 
function is not time-sensitive in reply or is async, SyncHttpRecorder is a good 
fit as shown below. If the function cannot afford to dispatch the span 
in-process, then it is recommended to either setup a haystack agent in the 
network and utilize HaystackAgentRecorder or offload the span record dispatching
via Queue -> Worker model. In AWS this could mean implementing a SQSRecorder 
which puts the finished span onto a SQS queue. The queue could then notify a 
lambda implementing SyncHttpRecorder to dispatch the records. 
"""

recorder = SyncHttpRecorder(os.env["COLLECTOR_URL"])

# suppose it is desired to tag all traces with the application version
common_tags = {
    "svc_ver": os["APP_VERSION"]
}
opentracing.tracer = HaystackTracer("example-service",
                                    recorder, common_tags=common_tags)


def invoke_downstream(headers):
    return "done"


def process_downstream_response(response):
    return "done"


def handler(event, context):

    # extract the span context from headers if this is a downstream service
    parent_ctx = opentracing.tracer.extract(opentracing.Format.HTTP_HEADERS,
                                            event)

    # now create a span representing the work of this entire function
    with opentracing.tracer.start_active_span("example-operation",
                                              child_of=parent_ctx) as request_scope:

        # log any important tags/baggage to the handler's span
        span = request_scope.span
        span.set_tag(tags.HTTP_URL, event["url"])
        span.set_tag(tags.SPAN_KIND, "server")

        # do some work (for ex. validation)
        # then log an event to the span which will timestamp the time taken up until this point
        span.log_kv({"validation_result": "success"})

        # an example of invoking a downstream service
        # Behind the scenes this uses the scope_manger to access the current active span and create a child of it.
        with opentracing.tracer.start_active_span("example-downstream-call") as child_scope:
            # span kind tags help haystack stitch and merge spans
            child_scope.span.set_tag(tags.SPAN_KIND, "client")

            headers = {
                "Content-Type": "application/json"
            }

            # inject the child span into the headers of downstream request
            opentracing.tracer.inject(child_scope.span.context, opentracing.Format.HTTP_HEADERS, headers)

            try:
                span.set_tag(tags.HTTP_URL, "https://downstream.url")
                response = invoke_downstream(headers)
            except RequestException:
                # when there's an issue a span can be tagged with error to flag it in haystack trends
                child_scope.span.set_tag(tags.ERROR, True)

        # be cognitive of which scope is handling the response processing. here we're back into the request_scope, thus
        # child_scope's span will only represent total time interacting with the downstream service
        lambda_response = process_downstream_response(response)

    return lambda_response
