import grpc
from proto.social_graph_pb2 import (
    FollowRequest,
    UnfollowRequest,
    GetFollowersRequest,
    GetFollowingRequest,
)
from proto.social_graph_pb2_grpc import SocialGraphServiceStub


def follow_user(follower, following, token):
    # with grpc.insecure_channel('127.0.0.1:50052') as channel:
    # with grpc.insecure_channel('tweety-server-1:50052') as channel:
    with grpc.insecure_channel('10.0.11.10:5002') as channel:
        stub = SocialGraphServiceStub(channel)
        response = stub.Follow(FollowRequest(follower_username=follower, following_username=following))
        return response


def unfollow_user(follower, following, token):
    # with grpc.insecure_channel('127.0.0.1:50052') as channel:
    # with grpc.insecure_channel('tweety-server-1:50052') as channel:
    with grpc.insecure_channel('10.0.11.10:5002') as channel:
        stub = SocialGraphServiceStub(channel)
        response = stub.Unfollow(UnfollowRequest(follower_username=follower, following_username=following))
        return response


def get_followers(username, token):
    # with grpc.insecure_channel('127.0.0.1:50052') as channel:
    # with grpc.insecure_channel('tweety-server-1:50052') as channel:
    with grpc.insecure_channel('10.0.11.10:5002') as channel:
        stub = SocialGraphServiceStub(channel)
        response = stub.GetFollowers(GetFollowersRequest(username=username))
        return response


def get_following(username, token):
    # with grpc.insecure_channel('127.0.0.1:50052') as channel:
    # with grpc.insecure_channel('tweety-server-1:50052') as channel:
    with grpc.insecure_channel('10.0.11.10:5002') as channel:
        stub = SocialGraphServiceStub(channel)
        response = stub.GetFollowing(GetFollowingRequest(username=username))
        return response
