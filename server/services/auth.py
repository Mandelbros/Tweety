from concurrent import futures
import grpc
from server.proto.auth_pb2 import RegisterResponse, LoginResponse
from server.proto.auth_pb2_grpc import AuthServiceServicer, add_AuthServiceServicer_to_server 
import hashlib 
import logging
from server.repository.auth import AuthRepository
import time, jwt

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
        username = request.user_id
        password = request.password_hash
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
        payload = {
            "exp": time.time() + 72 * 3600,
            "iss": "auth.service",
            "iat": time.time(),
            "email": user.email,
            "sub": user.username,
            "name": user.name
        }
        return jwt.encode(payload, self.jwt_priv_key, algorithm="RS256")

def start_auth(address, auth_repository: AuthRepository):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_AuthServiceServicer_to_server(AuthService(auth_repository), server)
   
    server.add_insecure_port(address)
    server.start()
    print("Auth server started or port 5001")    ### loggin remove
    server.wait_for_termination()

# def load_private_key():
#     with open(RSA_PRIVATE_KEY_PATH, "rb") as key_file:
#         private_key = serialization.load_pem_private_key(
#             key_file.read(),
#             password=PASSWORD.encode(),
#             backend=default_backend()
#         )
#     return private_key
