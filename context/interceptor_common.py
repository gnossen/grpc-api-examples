TRACING_LIBRARY_NAME = 'oxton'
TRACE_ID_KEY = f'{TRACING_LIBRARY_NAME}.trace_id'
PARENT_ID_KEY = f'{TRACING_LIBRARY_NAME}.parent_id'
SPAN_ID_KEY = f'{TRACING_LIBRARY_NAME}.span_id'

def generate_trace_id() -> Text:
    """Generates a trace ID according to a standards-defined algorithm."""

def generate_span_id() -> Text:
    """Generates a span ID according to a standards-defined algorithm."""
