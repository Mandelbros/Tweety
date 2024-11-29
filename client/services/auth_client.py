import grpc
from proto.auth_pb2 import RegisterRequest, LoginRequest
from proto.auth_pb2_grpc import AuthServiceStub

def register(username, password):
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = AuthServiceStub(channel)
        response = stub.Register(RegisterRequest(username=username, password=password))
        return response

def login(username, password):
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = AuthServiceStub(channel)
        response = stub.Login(LoginRequest(username=username, password=password))
        return response