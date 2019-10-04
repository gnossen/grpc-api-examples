# Implicit Context Propagation

Much has been said about context propagation for the gRPC Python asyncio API.
This is an example demonstrating my proposal for the shape of an API supporting
implicit context propagation.

Very little is actually expected from the gRPC library itself. The interceptor
API is essentially all that's needed. Middleware-defined server interceptors
install things into coroutine-local context using `contextvars` and
corresponding client interceptors read from `contextvars` and add them to
metadata.

The context object gives middleware a mechanism to store arbitrary key-value
pairs in a coroutine-local way without plumbing them through the application's
stack from server to client. But without middleware installed, *nothing* is
propagated by default, except timeout and cancellation, which are handled by the
gRPC library itself using `ContextVar` objects managed by the `gRPC` library
itself.

## Interceptors

Ancillary to the central point of context, but included in this example out of
necessity is a possible shape for `asyncio` interceptors. These are included
out of necessity, to demonstrate how tracing middleware will interface with
gRPC.

## Middleware

The files in this example are supposed to stand in for code from three different
authors. The first, is the application author. The application author owns the
following files:
 - `user.proto`
 - `server.py`
 - `client.py`

The "User" application makes use of a database with a gRPC interface. The
database author also owns several files in this example:

 - `db.proto`
 - `db_client.py`
 - `db.py`

Finally, a third-party has written a tracing library called "Oxton". They have
written and made avaiable gRPC interceptors in the following files:

 - `client_interceptors.py`
 - `server_interceptors.py`
 - `interceptor_common.py`

The only actual interaction with the context API happens in the previous two
files. Middleware authors are the only ones expected to touch it.
