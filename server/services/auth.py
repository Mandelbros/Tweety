from concurrent import futures
import grpc
from proto.auth_pb2 import RegisterResponse, LoginResponse
from proto.auth_pb2_grpc import AuthServiceServicer, add_AuthServiceServicer_to_server 
import hashlib 
import logging
from repository.auth import AuthRepository
import time, jwt, datetime, os

SECRET_KEY = "la llave secreta papu"

class AuthService(AuthServiceServicer):
    def __init__(self, auth_repository: AuthRepository, jwt_priv_key): 
        self.auth_repository = auth_repository
        self.jwt_priv_key = jwt_priv_key
        
    def Register(self, request, context): 
        user = request.user

        exists, err = self.auth_repository.exists_user(user.user_id)
        if exists or err:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Fallo al registrarse")

        self.auth_repository.save_user(user)
    
        logging.info("Registrado correctamente")
        return RegisterResponse(success=True, message="Usuario creado correctamente")

    def Login(self, request, context): 
        username = request.username
        password = request.password
        user, err = self.auth_repository.load_user(username)

        if err:
            if err == grpc.StatusCode.NOT_FOUND:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Nombre de usuario o contrasenna erronea")
            else:
                context.abort(err, "Algo salio mal")
            
        if not user or (user.password_hash != password):
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Nombre de usuario o contrasenna erronea")
 
        logging.info("Logueado de forma exitosa")
        token = self.gen_token(user)
        return LoginResponse(token=token)
    
    def gen_token(self, user):
        # Set token expiration time (e.g., 24 hours from now)
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        
        # Create token payload
        payload = {
            'user_id': user.user_id,
            'exp': expiration
        }
        token = jwt.encode(payload, self.jwt_priv_key, algorithm='HS256')
        return token

def start_auth(address, auth_repository: AuthRepository):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_AuthServiceServicer_to_server(AuthService(auth_repository, SECRET_KEY), server)
   
    server.add_insecure_port(address)
    server.start()
    print("Auth server started or port 5001")    ### loggin remove
    server.wait_for_termination()
