# Name of the HTTP header or Key used to encode Trace ID
TRACE_ID_HEADER = "Trace-ID"

# Name of the HTTP header or Key used to encode Span ID
SPAN_ID_HEADER = "Span-ID"

# Any additional header names to decode Span ID
ALTERNATE_SPAN_ID_HEADERS = ["Message-ID", ]

# Name of the HTTP header or Key used to encode Parent Span ID
PARENT_SPAN_ID_HEADER = "Parent-ID"

# Prefix of the HTTP header or Key used to encode Baggage items
BAGGAGE_HEADER_PREFIX = "Baggage-"

# The number of microseconds in one second
SECONDS_TO_MICRO = 1000000

# The default HTTP recorder timeout value
DEFAULT_HTTP_TIMEOUT = 5.0
