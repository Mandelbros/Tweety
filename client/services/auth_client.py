import grpc
from proto.auth_pb2 import RegisterRequest, LoginRequest
from proto.auth_pb2_grpc import AuthServiceStub
from proto import models_pb2
from discoverer import get_host
from config import AUTH
import logging

def register(username, email, name, password):
    host = get_host(AUTH)
    channel = grpc.insecure_channel(host)
    stub = AuthServiceStub(channel)
    user = models_pb2.User(user_id = username, email = email, name = name, password_hash = password)
    request = RegisterRequest(user=user)
    try:
        response = stub.Register(request)
        return True
    except grpc.RpcError as error:
        logging.error(f"An error occurred creating the user: {error.code()}: {error.details()}")
        return False
    
def login(username, password):
    host = get_host(AUTH)
    channel = grpc.insecure_channel(host)
    stub = AuthServiceStub(channel)
    request = LoginRequest(username=username, password=password)
    try:
        response = stub.Login(request)
        return response.token
    except grpc.RpcError as error:
        logging.error(f"An error occurred logging in: {error.code()}: {error.details()}")
        return None


