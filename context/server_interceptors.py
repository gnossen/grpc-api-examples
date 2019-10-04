import asyncio
import grpc
import grpc.aio
import logging
import time
import aiohttp

import interceptor_common

_BATCH_SIZE = 256
_TRACING_SERVER = 'tracing.grpc.io:80'

def _encode_batch(batch: Sequence[Tuple[Text, Text, Text, float]]) -> Text:
    """Encode the events into json or something like that."""

class TracingInterceptor(grpc.aio.ServerInterceptor):

    def __init__(self):
        self._ingress_log_queue = asyncio.Queue()
        self._tracing_server_session = aiohttp.ClientSession()

    async def _log_service_ingress(trace_id: Text, parent_id: Text, span_id: Text):
        ingress_time = time.time()
        # These logs will be dequeued by another coroutine and transmitted across the
        # network to a central tracing server.
        await self._ingress_log_queue.put((trace_id, parent_id, span_id, ingress_time))

    async def transmit_events(server_task: asyncio.Task):
        while not server_task.done():
            event_batch = []
            for _ in range(_BATCH_SIZE):
                event_batch.append(await self._ingress_log_queue.get())
            encoded_batch = _encoded_batch(event_batch)
            async with self._tracing_server_session.put(_TRACING_SERVER, encoded_batch) as response:
                text = await response.text()
                if response.status != 200:
                    logging.warning(f"Failed to send batch to server: {text}")


    async def intercept_service(self,
                                continuation: Callable[[grpc.aio.HandlerCallDetails], None],
                                handler_call_details: grpc.aio.HandlerCallDetails) -> grpc.aio.GenericRpcHandler:
        trace_id = None
        parent_id = None
        span_id = interceptor_common.generate_span_id()
        # Pull the appropriate values out of the request metadata.
        for key, value in handler_call_details.invocation_metadata:
            if key == interceptor_common.TRACE_ID_KEY:
                trace_id = value
            elif key == interceptor_common.PARENT_ID_KEY:
                parent_id = value
        if trace_id is None or parent_id is None:
            logging.warning("Received malformed tracing metadata.")
            # Continue the RPC nonetheless.
        else:
            # Inject the tracing data into the coroutine-local context.
            grpc.aio.set_context_value(interceptor_common.TRACE_ID_KEY, trace_id)
            grpc.aio.set_context_value(interceptor_common.PARENT_ID_KEY, parent_id)
            grpc.aio.set_context_value(interceptor_common.SPAN_ID_KEY, span_id)
            await _log_service_ingress(trace_id, parent_id, span_id)
        return await continuation(handler_call_details)

