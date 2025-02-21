import os
import grpc

from chord.node import Node
from server.repository.utils import save, load, delete, exists
from server.proto.models_pb2 import UserFollows 

class SocialGraphRepository:
    def __init__(self, node: Node) -> None:
        self.node = node

    def load_following_list(self, username):
        path = os.path.join("User", username.lower(), "Follow")
        user_follows, err = load(self.node, path, UserFollows())
        list = []
        if err == grpc.StatusCode.NOT_FOUND:
            return list, None

        if err:
            return None, grpc.StatusCode.INTERNAL("Failed to load following list: {}".format(err))

        for user_id in user_follows.followed_user_ids: 
            list.append(user_id)
        return list, None

    def add_to_following_list(self, username, followed_username):
        path = os.path.join("User", username.lower(), "Follow")
        user_follows, err = self.load_following_list(username)
        list = []
        if not err:
            list = user_follows

        if followed_username not in list:
            list.append(followed_username)
            err = save(self.node, UserFollows(followed_user_ids = list), path)

            if err:
                return False, grpc.StatusCode.INTERNAL("Failed to save following list: {}".format(err))

            return True, None

        return False, None

    def remove_from_following_list(self, username, followed_username):
        path = os.path.join("User", username.lower(), "Follow")
        user_follows, err = self.load_following_list(username)

        list = []

        if not err:
            list = user_follows

        if followed_username in list:
            list.remove(followed_username)
            err = save(self.node, UserFollows(followed_user_ids = list), path)

            if err:
                return False, grpc.StatusCode.INTERNAL("Failed to save following list: {}".format(err))

            return True, None

        return False, None
