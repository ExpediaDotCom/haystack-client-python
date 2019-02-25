from .span_pb2 import Span, Tag
import numbers

SECONDS_TO_MICRO = 1000000


def tags_as_list(tags):
    tag_list = []
    for key, value in tags.items():
        tag_list.append({"key": key, "value": value})
    return tag_list


def logs_as_list(logs):
    log_list = []
    for log_data in logs:
        kv_pairs = []
        for key, value in log_data.key_values.items():
            kv_pairs.append({"key": key, "value": value})
        log_list.append({"timestamp": int(log_data.timestamp * SECONDS_TO_MICRO), "fields": kv_pairs})
    return log_list


def set_tag_value(tag, value):
    if isinstance(value, numbers.Integral):
        tag.vLong = value
        tag.type = Tag.LONG
    elif isinstance(value, str):
        tag.vStr = value
        tag.type = Tag.STRING
    elif isinstance(value, bool):
        tag.vBool = value
        tag.type = Tag.BOOL
    elif isinstance(value, float):
        tag.vDouble = value
        tag.type = Tag.DOUBLE
    else:
        tag.vBytes = bytes("n/a", encoding="utf-8")  # TODO figure this out.
        tag.type = Tag.BINARY


def add_proto_tags(span_record, tags):
    for key, value in tags.items():
        tag = span_record.tags.add()
        tag.key = key
        set_tag_value(tag, value)


def add_proto_logs(span_record, logs):
    for log_data in logs:
        log_record = span_record.logs.add()
        log_record.timestamp = int(log_data.timestamp * SECONDS_TO_MICRO)
        for key, value in log_data.key_values.items():
            tag = log_record.fields.add()
            tag.key = key
            set_tag_value(tag, value)


def span_to_proto(span):
    span_record = Span(traceId=span.context.trace_id, spanId=span.context.span_id,
                       parentSpanId=span.context.parent_id, serviceName=span.tracer.service_name,
                       operationName=span.operation_name, startTime=int(span.start_time * SECONDS_TO_MICRO),
                       duration=int(span.duration * SECONDS_TO_MICRO))

    add_proto_tags(span_record, span.tags)
    add_proto_logs(span_record, span.logs)
    return span_record


def span_to_json(span):
    return {
        "traceId": span.context.trace_id,
        "spanId": span.context.span_id,
        "parentSpanId": span.context.parent_id,
        "serviceName": span.tracer.service_name,
        "operationName": span.operation_name,
        "startTime": int(span.start_time * SECONDS_TO_MICRO),
        "duration": int(span.duration * SECONDS_TO_MICRO),
        "tags": tags_as_list(span.tags),
        "logs": logs_as_list(span.logs)
    }


def span_to_string(span):
    record = "operation="
    record += span.operation_name
    record += ", traceid="
    record += span.context.trace_id
    record += ", spanid="
    record += span.context.span_id

    if span.context.parent_id:
        record += ", parentspanid="
        record += span.context.parent_id

    if span.context.baggage:
        record += str(span.context.baggage)

    if span.tags:
        record += ", tags=" + str(tags_as_list(span.tags))

    if span.logs:
        record += ", logs=" + str(logs_as_list(span.logs))

    record += ", starttime="
    record += str(int(span.start_time * SECONDS_TO_MICRO))
    record += ", duration="
    record += str(int(span.duration * SECONDS_TO_MICRO))

    return record
