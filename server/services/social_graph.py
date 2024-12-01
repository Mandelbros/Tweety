from concurrent import futures
import grpc
from server import shared_state
# from server.services.auth import users
from server.proto.social_graph_pb2 import (
    FollowResponse,
    UnfollowResponse,
    FollowersResponse,
    FollowingResponse,
)
from server.proto.social_graph_pb2_grpc import (
    SocialGraphServiceServicer,
    add_SocialGraphServiceServicer_to_server,
)

# In-memory storage for the social graph
# relationships = {
#     # Example structure: "user1": {"following": ["user2"], "followers": ["user3"]}
# } 

class SocialGraphService(SocialGraphServiceServicer):
    def Follow(self, request, context):
        follower = request.follower_username
        following = request.following_username

        if following not in shared_state.users:
            return FollowResponse(success=False, message="User to follow does not exist.")
        if follower == following:
            return FollowResponse(success=False, message="You cannot follow yourself.")

        # Add the following relationship
        shared_state.relationships.setdefault(follower, {"following": [], "followers": []})
        shared_state.relationships.setdefault(following, {"following": [], "followers": []})

        if following in shared_state.relationships[follower]["following"]:
            return FollowResponse(success=False, message="Already following this user.")

        shared_state.relationships[follower]["following"].append(following)
        shared_state.relationships[following]["followers"].append(follower)

        return FollowResponse(success=True, message="Successfully followed the user.")

    def Unfollow(self, request, context):
        follower = request.follower_username
        following = request.following_username

        if follower not in shared_state.relationships or following not in shared_state.relationships:
            return UnfollowResponse(success=False, message="User does not exist.")
        if following not in shared_state.relationships[follower]["following"]:
            return UnfollowResponse(success=False, message="Not following this user.")

        # Remove the following relationship
        shared_state.relationships[follower]["following"].remove(following)
        shared_state.relationships[following]["followers"].remove(follower)

        return UnfollowResponse(success=True, message="Successfully unfollowed the user.")

    def GetFollowers(self, request, context):
        username = request.username

        if username not in shared_state.relationships:
            return FollowersResponse(followers=[])

        return FollowersResponse(followers=shared_state.relationships[username]["followers"])

    def GetFollowing(self, request, context):
        username = request.username

        if username not in shared_state.relationships:
            return FollowingResponse(following=[])

        return FollowingResponse(following=shared_state.relationships[username]["following"])


def start_social_graph_service():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_SocialGraphServiceServicer_to_server(SocialGraphService(), server)
    server.add_insecure_port('127.0.0.1:50052')
    server.start()
    print("Social Graph Service started on port 50052") ### loggin remove
    server.wait_for_termination()
