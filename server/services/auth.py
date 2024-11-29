from concurrent import futures
import grpc
from server.proto.auth_pb2 import RegisterResponse, LoginResponse
from server.proto.auth_pb2_grpc import AuthServiceServicer, add_AuthServiceServicer_to_server 
import hashlib

users = {}

class AuthService(AuthServiceServicer):
    def Register(self, request, context):
        if request.username in users:
            return RegisterResponse(success=False, message="Username already exists")
        hashed_password = hashlib.sha256(request.password.encode()).hexdigest()
        users[request.username] = hashed_password
        print("succsesfully registered bro")    ### logging remove
        return RegisterResponse(success=True, message="User created successfully")

    def Login(self, request, context):
        if request.username not in users:
            return LoginResponse(success=False, message="User does not exist")
        hashed_password = hashlib.sha256(request.password.encode()).hexdigest()
        if users[request.username] != hashed_password:
            return LoginResponse(success=False, message="Incorrect password")
        return LoginResponse(success=True, message="Sign in successful")

def start_auth():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('127.0.0.1:50051')
    server.start
    print("Auth server started")    ### loggin remove
    server.wait_for_termination()
