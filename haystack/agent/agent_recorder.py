import grpc
import logging
from haystack.recorder import SpanRecorder
from haystack.agent import spanAgent_pb2_grpc
from haystack.util import span_to_proto

logger = logging.getLogger(__name__)


class HaystackAgentRecorder(SpanRecorder):

    def __init__(self, agent_host="haystack-agent", agent_port=35000):
        logger.info(f"Initializing the remote grpc agent recorder, connecting at {agent_host}:{agent_port}")
        channel = grpc.insecure_channel(f"{agent_host}:{agent_port}")
        self._stub = spanAgent_pb2_grpc.SpanAgentStub(channel)

    def record_span(self, span):
        try:
            grpc_response = self._stub.dispatch(span_to_proto(span))
            if grpc_response.code is not 0:
                logger.error(f"Dispatch failed with {grpc_response.code} due to {grpc_response.error_message}")
            else:
                logger.debug("Successfully submitted span to haystack-agent")
        except grpc.RpcError:
            logger.exception(f"Dispatch failed due to RPC error")
