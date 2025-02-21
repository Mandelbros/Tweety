import os
import grpc

from chord.node import Node
from server.repository.utils import save, load, delete, exists
from server.proto.models_pb2 import UserFollowing, UserFollowers

class SocialGraphRepository:
    def __init__(self, node: Node) -> None:
        self.node = node

    def load_following_list(self, username):
        path = os.path.join("User", username.lower(), "Following")
        user_following, err = load(self.node, path, UserFollowing())
        list = []
        if err == grpc.StatusCode.NOT_FOUND:
            return list, None

        if err:
            return None, grpc.StatusCode.INTERNAL("Failed to load following list: {}".format(err))

        for user_id in user_following.following_list: 
            list.append(user_id)
        return list, None

    def load_followers_list(self, username):
        path = os.path.join("User", username.lower(), "Followers")
        user_followers, err = load(self.node, path, UserFollowers())
        list = []
        if err == grpc.StatusCode.NOT_FOUND:
            return list, None

        if err:
            return None, grpc.StatusCode.INTERNAL("Failed to load followers list: {}".format(err))

        for user_id in user_followers.followers_list: 
            list.append(user_id)
        return list, None

    def add_to_following_list(self, username, followed_username):
        path = os.path.join("User", username.lower(), "Following")
        user_following, err = self.load_following_list(username)
        list = []
        if not err:
            list = user_following

        if followed_username not in list:
            list.append(followed_username)
            err = save(self.node, UserFollowing(following_list = list), path)

            if err:
                return False, grpc.StatusCode.INTERNAL("Failed to save following list: {}".format(err))

            return True, None

        return False, None

    def remove_from_following_list(self, username, followed_username):
        path = os.path.join("User", username.lower(), "Following")
        user_following, err = self.load_following_list(username)

        list = []

        if not err:
            list = user_following

        if followed_username in list:
            list.remove(followed_username)
            err = save(self.node, UserFollowing(following_list = list), path)

            if err:
                return False, grpc.StatusCode.INTERNAL("Failed to save following list: {}".format(err))

            return True, None

        return False, None
    
    def add_to_followers_list(self, username, follower_username):
        path = os.path.join("User", username.lower(), "Followers")
        user_followers, err = self.load_followers_list(username)

        list = []

        if not err:
            list = user_followers

        if follower_username not in list:
            list.append(follower_username)
            err = save(self.node, UserFollowers(followers_list = list), path)

            if err:
                return False, grpc.StatusCode.INTERNAL("Failed to save followers list: {}".format(err))

            return True, None

        return False, None

    def remove_from_followers_list(self, username, follower_username):
        path = os.path.join("User", username.lower(), "Followers")
        user_followers, err = self.load_followers_list(username)

        list = []

        if not err:
            list = user_followers

        if follower_username in list:
            list.remove(follower_username)
            err = save(self.node, UserFollowers(followers_list = list), path)

            if err:
                return False, grpc.StatusCode.INTERNAL("Failed to save followers list: {}".format(err))

            return True, None

        return False, None
