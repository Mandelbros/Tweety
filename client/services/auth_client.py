import grpc
from proto import auth_pb2, auth_pb2_grpc

def register(username, password):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        response = stub.Register(auth_pb2.RegisterRequest(username=username, password=password))
        return response

def login(username, password):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        response = stub.Login(auth_pb2.LoginRequest(username=username, password=password))
        return response