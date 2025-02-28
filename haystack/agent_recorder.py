import grpc
import logging
from haystack.recorder import SpanRecorder
from haystack.agent import spanAgent_pb2_grpc
from haystack.util import span_to_proto

logger = logging.getLogger(__name__)


class HaystackAgentRecorder(SpanRecorder):
    """
    HaystackAgentRecorder is to be used with the haystack-agent described
    """

    def __init__(self, agent_host="haystack-agent", agent_port=35000):
        logger.info("Initializing the remote grpc agent recorder, connecting "
                    f"at {agent_host}:{agent_port}")
        channel = grpc.insecure_channel(f"{agent_host}:{agent_port}")
        self._stub = spanAgent_pb2_grpc.SpanAgentStub(channel)

    @staticmethod
    def process_response(future):
        try:
            grpc_response = future.result()
            if grpc_response.code != 0:
                logger.error(f"Dispatch failed with {grpc_response.code} due "
                             f"to {grpc_response.error_message}")
            else:
                logger.debug("Successfully submitted span to haystack-agent")
        except grpc.RpcError:
            logger.exception("Dispatch failed due to RPC error")

    def record_span(self, span):
        future = self._stub.dispatch.future(span_to_proto(span))
        future.add_done_callback(HaystackAgentRecorder.process_response)
