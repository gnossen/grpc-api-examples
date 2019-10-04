import grpc
from proto import user_pb2, user_pb2_grpc
import db_client
import client_interceptors
import server_interceptors

HOST = '[::]:50051'
DB_TARGET = 'db.grpc.io:7777'

class UserService(user_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self._db_channel = grpc.intercept_channel(
                grpc.aio.insecure_channel(DB_TARGET),
                tracing_interceptors.tracing_interceptor())

    async def CreateUser(self,
                         request: user_pb2.CreateUserRequest,
                         context: grpc.aio.ServicerContext):
        record = await db_client.create_record(request.name, self._db_channel)
        return user_pb2.CreateUserResponse(
                user=user_pb2.User(id=record.id,
                                   value=record.value))


async def run_server():
    tracing_interceptor = server_interceptors.TracingInterceptor()
    server = grpc.aio.server(interceptors=(tracing_interceptor))
    server.add_insecure_port(HOST)
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    stop_event = server.stop_event()
    server.start()
    server_task = asyncio.create_task(server.wait_for_termination())
    await asyncio.gather(
        server_task,
        tracing_interceptor.transmit_events(server_task),
    )


def main():
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
