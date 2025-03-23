import grpc
from proto.social_graph_pb2 import (
    FollowRequest,
    UnfollowRequest,
    GetFollowersRequest,
    GetFollowingRequest,
)
from proto.social_graph_pb2_grpc import SocialGraphServiceStub
from discoverer import get_host, get_authenticated_channel
from config import SOCIAL_GRAPH
import logging
from cache import FileCache

def follow_user(follower_id, followed_id, token):
    host = get_host(SOCIAL_GRAPH)
    channel = get_authenticated_channel(host ,token)
    stub = SocialGraphServiceStub(channel)
    request = FollowRequest(follower_id=follower_id, followed_id=followed_id)
    try:
        response = stub.Follow(request)
        return response
    except grpc.RpcError as error:
        logging.error(f"An error occurred following the user: {error.code()}: {error.details()}")
        return False
    
def unfollow_user(follower_id, followed_id, token):
    host = get_host(SOCIAL_GRAPH)
    channel = get_authenticated_channel(host ,token)
    stub = SocialGraphServiceStub(channel)
    request = UnfollowRequest(follower_id=follower_id, followed_id=followed_id)
    try:
        response = stub.Unfollow(request)
        return response
    except grpc.RpcError as error:
        logging.error(f"An error occurred unfollowing the user: {error.code()}: {error.details()}")
        return False

async def get_followers(username, token, request = False):
    # if not request:
    #     cached_followers = await FileCache.get(f"{username}_followers")
    #     if cached_followers is not None:
    #         return cached_followers
        
    host = get_host(SOCIAL_GRAPH)
    channel = get_authenticated_channel(host ,token)
    stub = SocialGraphServiceStub(channel)
    request = GetFollowersRequest(user_id=username)

    try:
        response = stub.GetFollowers(request)
        followers_list = [username for username in response.followers_list] 
        # await FileCache.set(f"{username}_followers", followers_list)
        return response.followers_list
    except grpc.RpcError as error:
        logging.error(f"An error occurred fetching the followers list: {error.code()}: {error.details()}")
        return None

async def get_following(username, token, request = False):
    # if not request:
    #     cached_following = await FileCache.get(f"{username}_following")
    #     if cached_following is not None:
    #         return cached_following
        
    host = get_host(SOCIAL_GRAPH)
    channel = get_authenticated_channel(host ,token)
    stub = SocialGraphServiceStub(channel)
    request = GetFollowingRequest(user_id=username)

    try:
        response = stub.GetFollowing(request)
        following_list = [username for username in response.following_list] 
        # await FileCache.set(f"{username}_following", following_list)
        return response.following_list
    except grpc.RpcError as error:
        logging.error(f"An error occurred fetching the following list: {error.code()}: {error.details()}")
        return None