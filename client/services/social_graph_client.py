import grpc
from proto.social_graph_pb2 import (
    FollowRequest,
    UnfollowRequest,
    FollowersRequest,
    FollowingRequest,
)
from proto.social_graph_pb2_grpc import SocialGraphServiceStub


def follow_user(follower, following):
    with grpc.insecure_channel('127.0.0.1:50052') as channel:
        stub = SocialGraphServiceStub(channel)
        response = stub.Follow(FollowRequest(follower_username=follower, following_username=following))
        return response


def unfollow_user(follower, following):
    with grpc.insecure_channel('127.0.0.1:50052') as channel:
        stub = SocialGraphServiceStub(channel)
        response = stub.Unfollow(UnfollowRequest(follower_username=follower, following_username=following))
        return response


def get_followers(username):
    with grpc.insecure_channel('127.0.0.1:50052') as channel:
        stub = SocialGraphServiceStub(channel)
        response = stub.GetFollowers(FollowersRequest(username=username))
        return response


def get_following(username):
    with grpc.insecure_channel('127.0.0.1:50052') as channel:
        stub = SocialGraphServiceStub(channel)
        response = stub.GetFollowing(FollowingRequest(username=username))
        return response
