import time
import uuid
from opentracing import Format, Tracer, UnsupportedFormatException
from opentracing.scope_managers import ThreadLocalScopeManager
from .text_propagator import TextPropagator
from .span import Span, SpanContext


class HaystackTracer(Tracer):

    def __init__(self,
                 service_name,
                 recorder,
                 scope_manager=None,
                 common_tags=None,
                 use_shared_spans=False):
        """
        Initialize a Haystack Tracer instance.
        :param service_name: The service name to which all spans will belong.
        :param recorder: The recorder (dispatcher) implementation which handles
        finished spans.
        :param scope_manager: An optional parameter to override the default
        ThreadLocal scope manager.
        :param common_tags: An optional dictionary of tags which should be
        applied to all created spans for this service
        :param use_shared_spans: A boolean indicating whether or not to use
        shared spans. This is when client/server spans share the same span id.
        Default is to use unique span ids.
        """

        scope_manager = ThreadLocalScopeManager() if scope_manager is None \
            else scope_manager
        super().__init__(scope_manager)
        self._propagators = {}
        self._common_tags = {} if common_tags is None else common_tags
        self.service_name = service_name
        self.recorder = recorder
        self.use_shared_spans = use_shared_spans
        self.register_propagator(Format.TEXT_MAP, TextPropagator())
        self.register_propagator(Format.HTTP_HEADERS, TextPropagator())

    def register_propagator(self, format, propagator):
        """Register a propagator with this Tracer.

        :param string format: a Format identifier like Format.TEXT_MAP
        :param Propagator propagator: a Propagator instance to handle
            inject/extract calls
        """
        self._propagators[format] = propagator

    def start_active_span(self,
                          operation_name,
                          child_of=None,
                          references=None,
                          tags=None,
                          start_time=None,
                          ignore_active_span=False,
                          finish_on_close=True):

        span = self.start_span(operation_name=operation_name,
                               child_of=child_of,
                               references=references,
                               tags=tags,
                               start_time=start_time,
                               ignore_active_span=ignore_active_span)

        return self.scope_manager.activate(span, finish_on_close)

    def start_span(self,
                   operation_name=None,
                   child_of=None,
                   references=None,
                   tags=None,
                   start_time=None,
                   ignore_active_span=False):

        start_time = time.time() if start_time is None else start_time

        # Check for an existing ctx in `references`
        parent_ctx = None
        if child_of is not None:
            parent_ctx = (child_of if isinstance(child_of, SpanContext)
                          else child_of.context)
        elif references is not None and len(references) > 0:
            parent_ctx = references[0].referenced_context

        # Check for an active span in scope manager
        if not ignore_active_span and parent_ctx is None:
            scope = self.scope_manager.active
            if scope is not None:
                parent_ctx = scope.span.context

        new_ctx = SpanContext(span_id=format(uuid.uuid4()))
        if parent_ctx is not None:
            new_ctx.trace_id = parent_ctx.trace_id
            if parent_ctx.baggage is not None:
                new_ctx._baggage = parent_ctx.baggage.copy()
            if self.use_shared_spans:
                new_ctx.span_id = parent_ctx.span_id
                new_ctx.parent_id = parent_ctx.parent_id
            else:
                new_ctx.parent_id = parent_ctx.span_id
        else:
            new_ctx.trace_id = format(uuid.uuid4())

        # Set common tags
        if self._common_tags:
            tags = {**self._common_tags, **tags} if tags else \
                self._common_tags.copy()

        return Span(self,
                    operation_name=operation_name,
                    context=new_ctx,
                    tags=tags,
                    start_time=start_time)

    def inject(self, span_context, format, carrier):
        if format in self._propagators:
            self._propagators[format].inject(span_context, carrier)
        else:
            raise UnsupportedFormatException()

    def extract(self, format, carrier):
        if format in self._propagators:
            return self._propagators[format].extract(carrier)
        else:
            raise UnsupportedFormatException()

    def record(self, span):
        self.recorder.record_span(span)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
