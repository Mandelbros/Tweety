import logging
import grpc
from concurrent import futures
from server.proto.social_graph_pb2_grpc import SocialGraphServiceServicer, add_SocialGraphServiceServicer_to_server
from server.proto.social_graph_pb2 import FollowResponse, UnfollowResponse, GetFollowingResponse, GetFollowersResponse 
from server.repository.auth import AuthRepository
from server.repository.social_graph import SocialGraphRepository

class SocialGraphService(SocialGraphServiceServicer):
    def __init__(self, social_graph_repository:SocialGraphRepository, auth_repository:AuthRepository):
        self.social_graph_repository = social_graph_repository
        self.auth_repository = auth_repository

    def Follow(self, request, context):
        username = request.follower_id
        followed_username  = request.followed_id

        if username == followed_username:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Cannot follow yourself")

        if not self.auth_repository.exists_user(username):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        if not self.auth_repository.exists_user(followed_username):
            context.abort(grpc.StatusCode.NOT_FOUND, "Target user not found")

        ok, err = self.social_graph_repository.add_to_following_list(username, followed_username)

        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to follow user: {err}")

        if not ok:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Already following user {followed_username}")

        ok, err = self.social_graph_repository.add_to_followers_list(followed_username, username)

        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to follow user: {err}")

        if not ok:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, f"User already a follower {username}")

        return FollowResponse()

    def Unfollow(self, request, context):
        username = request.user_id
        unfollowed_username = request.unfollowed_id

        if username == unfollowed_username:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Cannot unfollow yourself")

        if not self.auth_repository.exists_user(username):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        if not self.auth_repository.exists_user(unfollowed_username):
            context.abort(grpc.StatusCode.NOT_FOUND, "Target user not found")

        ok, err = self.social_graph_repository.remove_from_following_list(username, unfollowed_username)

        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to unfollow user: {err}")

        if not ok:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Not following user {unfollowed_username}")

        ok, err = self.social_graph_repository.remove_from_followers_list(unfollowed_username, username)

        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to unfollow user: {err}")

        if not ok:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Not a follower {username}")

        return UnfollowResponse()

    def GetFollowing(self, request, context):
        username = request.user_id

        if not self.auth_repository.exists_user(username):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        list, err = self.social_graph_repository.load_following_list(username)

        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to load following list: {err}")

        return GetFollowingResponse(following_list=list)

    def GetFollowers(self, request, context):
        username = request.user_id

        if not self.auth_repository.exists_user(username):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        list, err = self.social_graph_repository.load_followers_list(username)

        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to load followers list: {err}")

        return GetFollowersResponse(followers_list=list)


def start_social_graph_service(social_graph_repository:SocialGraphRepository, auth_repository:AuthRepository):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_SocialGraphServiceServicer_to_server(SocialGraphService(social_graph_repository, auth_repository), server)
    # server.add_insecure_port('0.0.0.0:50052')
    server.add_insecure_port('10.0.11.10:5002')
    server.start()
    logging.info("Social Graph Service started on port 5002")
    server.wait_for_termination()

