from concurrent import futures
import grpc
from server.services.auth import users
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
relationships = {
    # Example structure: "user1": {"following": ["user2"], "followers": ["user3"]}
}


class SocialGraphService(SocialGraphServiceServicer):
    def Follow(self, request, context):
        follower = request.follower_username
        following = request.following_username

        if following not in users:
            return FollowResponse(success=False, message="User to follow does not exist.")
        if follower == following:
            return FollowResponse(success=False, message="You cannot follow yourself.")

        # Add the following relationship
        relationships.setdefault(follower, {"following": [], "followers": []})
        relationships.setdefault(following, {"following": [], "followers": []})

        if following in relationships[follower]["following"]:
            return FollowResponse(success=False, message="Already following this user.")

        relationships[follower]["following"].append(following)
        relationships[following]["followers"].append(follower)

        return FollowResponse(success=True, message="Successfully followed the user.")

    def Unfollow(self, request, context):
        follower = request.follower_username
        following = request.following_username

        if follower not in relationships or following not in relationships:
            return UnfollowResponse(success=False, message="User does not exist.")
        if following not in relationships[follower]["following"]:
            return UnfollowResponse(success=False, message="Not following this user.")

        # Remove the following relationship
        relationships[follower]["following"].remove(following)
        relationships[following]["followers"].remove(follower)

        return UnfollowResponse(success=True, message="Successfully unfollowed the user.")

    def GetFollowers(self, request, context):
        username = request.username

        if username not in relationships:
            return FollowersResponse(followers=[])

        return FollowersResponse(followers=relationships[username]["followers"])

    def GetFollowing(self, request, context):
        username = request.username

        if username not in relationships:
            return FollowingResponse(following=[])

        return FollowingResponse(following=relationships[username]["following"])


def start_social_graph_service():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_SocialGraphServiceServicer_to_server(SocialGraphService(), server)
    server.add_insecure_port('127.0.0.1:50052')
    server.start()
    print("Social Graph Service started on port 50052")
    server.wait_for_termination()
