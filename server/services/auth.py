from concurrent import futures
import grpc
from server.proto.auth_pb2 import RegisterResponse, LoginResponse
from server.proto.auth_pb2_grpc import AuthServiceServicer, add_AuthServiceServicer_to_server 
import hashlib 
import logging
from server.repository.auth import AuthRepository

class AuthService(AuthServiceServicer):
    def __init__(self, auth_repository: AuthRepository): 
        self.auth_repository = auth_repository
        
    def Register(self, request, context): 
        user = request.user

        exists, err = self.auth_repository.exists_user(user.username)
        if exists or err:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Fail to sign up")

        self.auth_repository.save_user(user)
    
        logging.info("Succesfully registered")
        return RegisterResponse(success=True, message="User created successfully")

    def Login(self, request, context): 
        username = request.username
        password = request.password
        user, err = self.auth_repository.load_user(username)

        if err:
            if err == grpc.StatusCode.NOT_FOUND:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Wrong username or password")
            else:
                context.abort(err, "Something went wrong")
            
        if not user or (user.password_hash != password):
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Wrong username or password")
 
        logging.info("Succesfully logged in")
        return LoginResponse(success=True, message="Sign in successful")

def start_auth(auth_repository: AuthRepository):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_AuthServiceServicer_to_server(AuthService(auth_repository), server)
    # server.add_insecure_port('0.0.0.0:50051')
    server.add_insecure_port('10.0.11.10:5001')
    server.start()
    print("Auth server started or port 5001")    ### loggin remove
    server.wait_for_termination()
