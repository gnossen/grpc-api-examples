import grpc
from proto import db_pb2, db_pb2_grpc


# NOTE: This file is meant to stand in for a third-party DB client library.
# Importantly, assume that this file does not lie under the same domain of
# control as client.py or server.py and, as such, changes to this file have
# a substantially higher cost.
async def create_record(value: Text, channel: grpc.Channel) -> db_pb2.Record:
    stub = db_pb2_grpc.RecordServiceStub(channel)
    response = await stub.Create(db_pb2.CreateRequest(value=value))
    return response.record
