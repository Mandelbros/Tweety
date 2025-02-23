import os
import grpc
from chord.node import Node
from repository.utils import save, load, exists
from proto.models_pb2 import User 

class AuthRepository:
    def __init__(self, node: Node) -> None:
        self.node = node

    def exists_user(self, username: str):
        path = os.path.join("User", username.lower())
        return exists(self.node, path)

    def load_user(self, username: str):
        path = os.path.join("User", username.lower())
        user, err = load(self.node, path, User())

        if err == grpc.StatusCode.NOT_FOUND:
            return None, grpc.StatusCode.NOT_FOUND
        elif err:
            return None, grpc.StatusCode.INTERNAL

        return user, None

    def save_user(self, user):
        path = os.path.join("User", user.username.lower())
        err = save(self.node, user, path)

        if err:
            return grpc.StatusCode.INTERNAL

        return None