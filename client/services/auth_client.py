import grpc
from proto.auth_pb2 import RegisterRequest, LoginRequest
from proto.auth_pb2_grpc import AuthServiceStub

def register(username, password):
    try:
        # with grpc.insecure_channel('127.0.0.1:50051') as channel:
        # with grpc.insecure_channel('tweety-server-1:50051') as channel:
        with grpc.insecure_channel('10.0.11.10:5001') as channel:
            stub = AuthServiceStub(channel)
            response = stub.Register(RegisterRequest(username=username, password=password))
            return response
    except grpc.RpcError as e:
        print(f"gRPC error: {e}")
        return None

def login(username, password):
    try:
        # with grpc.insecure_channel('127.0.0.1:50051') as channel:
        # with grpc.insecure_channel('tweety-server-1:50051') as channel:
        with grpc.insecure_channel('10.0.11.10:5001') as channel:
            stub = AuthServiceStub(channel)
            response = stub.Login(LoginRequest(username=username, password=password))
            return response
    except grpc.RpcError as e:
        print(f"gRPC error: {e}")
        return None