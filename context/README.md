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

While these functions use `contextvars` behind the scenes, this is just an
implementation detail. Behind the scenes, all keys are backed by a single
`ContextVar` object, segregated by key. Each key enjoys the same copy-on-write
properties as the default `ContextVars` objects do:

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

Ancillary to the central point of context, but included in this example out of
necessity is a possible shape for `asyncio` interceptors. These are included
out of necessity, to demonstrate how tracing middleware will interface with
gRPC.
