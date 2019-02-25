from abc import ABC, abstractmethod


class Propagator(ABC):

    @abstractmethod
    def inject(self, span_context, carrier):
        pass

    @abstractmethod
    def extract(self, carrier):
        pass
