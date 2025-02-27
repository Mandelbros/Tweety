import grpc
from proto.message_pb2 import PostMessageRequest, GetMessagesRequest, RepostMessageRequest
from proto.message_pb2_grpc import MessageServiceStub

def post_message(username, content, token):
    try:
        # with grpc.insecure_channel('127.0.0.1:50053') as channel:
        # with grpc.insecure_channel('tweety-server-1:50053') as channel:
        with grpc.insecure_channel('10.0.11.10:5003') as channel:
            stub = MessageServiceStub(channel)
            response = stub.PostMessage(PostMessageRequest(username=username, content=content))
            return response
    except grpc.RpcError as e:
        print(f"gRPC error: {e}")
        return None

def get_messages(username, token):
    try:
        # with grpc.insecure_channel('127.0.0.1:50053') as channel:
        # with grpc.insecure_channel('tweety-server-1:50053') as channel:
        with grpc.insecure_channel('10.0.11.10:5003') as channel:
            stub = MessageServiceStub(channel)
            response = stub.GetMessages(GetMessagesRequest(username=username))
            return response
    except grpc.RpcError as e:
        print(f"gRPC error: {e}")
        return None

def repost_message(username, original_message_id, token):
    try:
        # with grpc.insecure_channel('127.0.0.1:50053') as channel:
        # with grpc.insecure_channel('tweety-server-1:50053') as channel:
        with grpc.insecure_channel('10.0.11.10:5003') as channel:
            stub = MessageServiceStub(channel)
            response = stub.RepostMessage(RepostMessageRequest(username=username, original_message_index=original_message_id))
            return response
    except grpc.RpcError as e:
        print(f"gRPC error: {e}")
        return None
