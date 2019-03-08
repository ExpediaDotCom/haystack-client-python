from abc import ABC, abstractmethod
from collections import namedtuple
from .constants import (
    TRACE_ID,
    SPAN_ID,
    PARENT_SPAN_ID,
    BAGGAGE_PREFIX,
)


class Propagator(ABC):

    @abstractmethod
    def inject(self, span_context, carrier):
        raise NotImplementedError()

    @abstractmethod
    def extract(self, carrier):
        raise NotImplementedError()


PropagatorOpts = namedtuple("PropagatorOpts", ["trace_id_key",
                                               "span_id_key",
                                               "parent_id_key",
                                               "baggage_key_prefix"])
PropagatorOpts.__new__.__defaults__ = (TRACE_ID, SPAN_ID, PARENT_SPAN_ID,
                                       BAGGAGE_PREFIX)
