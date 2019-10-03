import asyncio
import datetime
import grpc
from proto import user_pb2, user_pb2_grpc
import client_interceptors

SERVER_TARGET = 'users.grpc.io:50051'

async def create_user():
    tracing_interceptor = tracing_interceptors.probabilistic_tracing_interceptor()
    async with grpc.intercept_channel(
            grpc.insecure_channel(SERVER_TARGET),
            tracing_interceptor) as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        new_user = user_pb2.CreateUserRequest(
                name="Smitty Werbenjagermanjensen")
        # The timeout will implicitly be propagated through the following files:
        #  - client.py
        #  - server.py
        #  - db_client.py
        #  - db.py
        # 
        # If a timeout occurs at any link in that chain, an exception will be
        # raised from the call to stub.CreateUser and an on_done callback will
        # be executed in the service handlers in server.py and db.py, allowing
        # the user to exit their coroutines using, e.g. asyncio.Event.
        response = await stub.CreateUser(new_user,
                                         timeout=datetime.timedelta(seconds=3))
        print(f"Successfully created user {response.user.name} with id {response.user.id}.")


def main():
    asyncio.run(create_user())

if __name__ == "__main__":
    main()
