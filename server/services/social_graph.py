import logging
import grpc
from concurrent import futures
from proto.social_graph_pb2_grpc import SocialGraphServiceServicer, add_SocialGraphServiceServicer_to_server
from proto.social_graph_pb2 import FollowResponse, UnfollowResponse, GetFollowingResponse, GetFollowersResponse 
from repository.auth import AuthRepository
from repository.social_graph import SocialGraphRepository

class SocialGraphService(SocialGraphServiceServicer):
    def __init__(self, social_graph_repository: SocialGraphRepository, auth_repository: AuthRepository):
        self.social_graph_repository = social_graph_repository
        self.auth_repository = auth_repository

    def Follow(self, request, context):
        username = request.follower_id
        followed_username = request.followed_id

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
            return FollowResponse(success=False, message=f"Already following user {followed_username}")

        ok, err = self.social_graph_repository.add_to_followers_list(followed_username, username)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to follow user: {err}")
        if not ok:
            return FollowResponse(success=False, message=f"User {username} is already a follower")

        return FollowResponse(success=True, message=f"Successfully followed {followed_username}")

    def Unfollow(self, request, context):
        username = request.follower_id
        unfollowed_username = request.followed_id

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
            return UnfollowResponse(success=False, message=f"Not following user {unfollowed_username}")

        ok, err = self.social_graph_repository.remove_from_followers_list(unfollowed_username, username)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to unfollow user: {err}")
        if not ok:
            return UnfollowResponse(success=False, message=f"User {username} is not a follower")

        return UnfollowResponse(success=True, message=f"Successfully unfollowed {unfollowed_username}")

    def GetFollowing(self, request, context):
        username = request.user_id

        if not self.auth_repository.exists_user(username):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        following_list, err = self.social_graph_repository.load_following_list(username)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to load following list: {err}")

        return GetFollowingResponse(following_list=following_list)

    def GetFollowers(self, request, context):
        username = request.user_id

        if not self.auth_repository.exists_user(username):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        followers_list, err = self.social_graph_repository.load_followers_list(username)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to load followers list: {err}")

        return GetFollowersResponse(followers_list=followers_list)


def start_social_graph_service(address, social_graph_repository:SocialGraphRepository, auth_repository:AuthRepository):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_SocialGraphServiceServicer_to_server(SocialGraphService(social_graph_repository, auth_repository), server)
    server.add_insecure_port(address)
    server.start()
    logging.info("Social Graph Service started on port 5002")
    server.wait_for_termination()

