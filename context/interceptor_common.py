# NOTE: The library name is used in context keys to ensure we do not clash with
# any other libraries that may be populating the context object.

import contextvars

TRACING_LIBRARY_NAME = 'oxton'
TRACE_ID_KEY = f'{TRACING_LIBRARY_NAME}.trace_id'
PARENT_ID_KEY = f'{TRACING_LIBRARY_NAME}.parent_id'
SPAN_ID_KEY = f'{TRACING_LIBRARY_NAME}.span_id'

TRACE_ID_CONTEXTVAR = contextvars.ContextVar(TRACE_ID_KEY)
PARENT_ID_CONTEXTVAR = contextvars.ContextVar(PARENT_ID_KEY)
SPAN_ID_KEY = contextvars.ContextVar(SPAN_ID_KEY)

def generate_trace_id() -> Text:
    """Generates a trace ID according to a standards-defined algorithm."""

def generate_span_id() -> Text:
    """Generates a span ID according to a standards-defined algorithm."""
