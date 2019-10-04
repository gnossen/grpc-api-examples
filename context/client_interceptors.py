import grpc
import grpc.aio

import random

from typing import Any, AsyncGenerator, Tuple

import interceptor_common

_DEFAULT_TRACING_PROBABLIITY = 0.5

# NOTE: This file is meant as a stand-in for third party tracing middleware,
# e.g. OpenCensus (https://opencensus.io/). Different libraries have different
# opinions on the data that should be tracked by each request and what
# percentage of requests should be traced.

def tracing_interceptor() -> grpc.aio.GenericClientInterceptor:
    return probabilistic_tracing_interceptor(1.0)


def probabilistic_tracing_interceptor(
        tracing_probability: float = _DEFAULT_TRACING_PROBABILITY) -> grpc.aio.GenericClientInterceptor:
    """ Create an interceptor that tracks a supplied percentage of requests.

    This interceptor should only be used upon ingress to the system. All
    intermediary services should use an unconditional interceptor.

    Args:
      tracing_probability: A value in the range [0.0, 1.0] representing the
        fraction of requests whose transit through the system will be traced.
    """
    # NOTE: The return type here closely mirrors the original
    # GenericClientInterceptor interface. We may want to clean it up.
    def intercept_call(client_call_details: grpc.aio.ClientCallDetails,
                       request_generator: AsyncGenerator[Any, Any, Any]
                       request_streaming: bool,
                       response_streaming: bool) -> Tuple[grpc.aio.ClientCallDetails,
                                                          AsyncGenerator[Any, Any, Any],
                                                          Callable[AsyncGenerator[Any, Any, Any]]]
        metadata = client_call_details.metadata or []
        if random.random() < tracing_probability:
            # Tag this request.

            trace_id = interceptor_common.TRACE_ID_CONTEXTVAR.get()
            parent_id = None
            if trace_id is None:
                # This request has no parent. Generate a new trace ID.
                trace_id = interceptor_common.generate_trace_id()
            else:
                parent_id = interceptor_common.SPAN_ID_CONTEXTVAR.get()
            for key, value in ((interceptor_common.TRACE_ID_KEY, trace_id),
                               (interceptor_common.PARENT_ID_KEY, parent_id)):
                if value is not None:
                    metadata.append((key, value))
        # TODO: We might want a better way to construct one of these from an
        # existing ClientCallDetails object. This current API very closely
        # mirrors the existing interceptor API.
        new_client_call_details = grpc.aio.ClientCallDetails(client_call_details.method,
                                                             client_call_details.timeout,
                                                             metadata,
                                                             client_call_details.credentials)
        return new_client_call_details, request_generator, None

    return grpc.aio.generic_client_interceptor(intercept_call)
