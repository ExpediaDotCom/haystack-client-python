from .propagator import Propagator


# TODO build me for IPC purposes (use TextPropagator instead for now)
class BinaryPropagator(Propagator):
    """A propagator for Format.BINARY"""

    def inject(self, span_context, carrier):
        pass

    def extract(self, carrier):
        pass
