# Implicit Context Propagation

Much has been said about context propagation for the gRPC Python asyncio API.
This is an example demonstrating my proposal for the shape of an API supporting
implicit context propagation.

The core of the API is really two functions (whose names I leave open to
bikeshedding):

```python
# module grpc.aio
def get_context_value(key: Text) -> Optional[Text]:
    """Get a value associated with a key from the coroutine-local context."""

def set_context_value(key: Text, value: Text):
    """Sets a value associated with a key in the coroutine-local context."""
```

Behind the scenes, all keys are backed by a single `contextvars.ContextVar` object,
segregated by key. Each key enjoys the same copy-on-write properties as the
default `ContextVars` objects do. However, usage of `contextvars` is *just* an
implementation detail. Note that the user is never exposed to any functions or
objects from the `contextvars` API.

```python
async def func1():
  print("func1")
  print(grpc.aio.get_context_value("foo"))
  grpc.aio.set_context_value("foo", "func1")
  print(grpc.aio.get_context_value("foo"))

async def func2():
  print("func2")
  print(grpc.aio.get_context_value("foo"))
  grpc.aio.set_context_value("foo", "func2")
  print(grpc.aio.get_context_value("foo"))

async def func3():
  print("func3")
  print(grpc.aio.get_context_value("foo"))
  grpc.aio.set_context_value("foo", "func3")
  print(grpc.aio.get_context_value("foo"))

async def main():
  grpc.aio.set_context_value("foo", "default")
  await asyncio.gather(
    func1(),
    func2(),
    func3()
  )
  print("After gather")
  print(grpc.aio.get_context_value("foo"))

asyncio.run(main())
```

```
func1
default
func1
func2
default
func2
func3
default
func3
After gather
default
```

The context object gives middleware a mechanism to store arbitrary key-value
pairs in a coroutine-local way without plumbing them through the application's
stack from server to client. But without middleware installed, *nothing* is
propagated by default, except timeout and cancellation, which are handled by the
gRPC library itself.

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
