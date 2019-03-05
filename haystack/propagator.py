from abc import ABC, abstractmethod


class Propagator(ABC):

    @abstractmethod
    def inject(self, span_context, carrier):
        raise NotImplementedError()

    @abstractmethod
    def extract(self, carrier):
        raise NotImplementedError()
