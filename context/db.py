import asyncio
import grpc
from proto import db_pb2, db_pb2_grpc

HOST = '[::]:7777'

IN_MEMORY_RECORDS = {
    0: 'root',
    1: 'Kevin Flynn',
    2: 'Hiro Protagonist',
}
MAX_ID = max(IN_MEMORY_RECORDS)


class RecordService(db_pb2_grpc.RecordServiceServicer):
    async def Create(self,
                     request: db_pb2.CreateRequest,
                     context: grpc.aio.ServicerContext):
        done_event = asyncio.Event()
        def on_done():
            done_event.set()
        global MAX_ID
        new_id = None
        if value in _IN_MEMORY_RECORDS.values():
            context.abort(grpc.StatusCode.ALREADY_EXISTS,
                          f"Value '{request.value}' already exists.")
        MAX_ID += 1
        new_id = MAX_ID
        IN_MEMORY_RECORDS[new_id] = request.value
        # Pretend we have a lot more work to do here. This just demonstrates
        # what the application author must do to cooperate with cancellation.
        if done_event.is_set():
            return
        return db_pb2.Record(id=new_id, value=request.value)


async def run_server():
    server = grpc.aio.server()
    server.add_insecure_port(HOST)
    user_pb2_grpc.add_RecordServiceServicer_to_server(RecordService(), server)
    server.start()
    await server.wait_for_termination()


def main():
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
