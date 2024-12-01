import grpc
from proto.message_pb2 import PostMessageRequest, GetMessagesRequest
from proto.message_pb2_grpc import MessageServiceStub

def post_message(username, content):
    try:
        with grpc.insecure_channel('127.0.0.1:50053') as channel:
            stub = MessageServiceStub(channel)
            response = stub.PostMessage(PostMessageRequest(username=username, content=content))
            return response
    except grpc.RpcError as e:
        print(f"gRPC error: {e}")
        return None

def get_messages(username=None):
    try:
        with grpc.insecure_channel('127.0.0.1:50053') as channel:
            stub = MessageServiceStub(channel)
            response = stub.GetMessages(GetMessagesRequest(username=username))
            return response
    except grpc.RpcError as e:
        print(f"gRPC error: {e}")
        return None
