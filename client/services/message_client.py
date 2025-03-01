import grpc
from proto.message_pb2 import PostMessageRequest, GetMessagesRequest, RepostMessageRequest
from proto.message_pb2_grpc import MessageServiceStub 
from cache import FileCache
from config import POST
from discoverer import get_host, get_authenticated_channel
from proto import models_pb2
import logging

async def get_messages(username, token, request=True):
    if not request:
        cached_posts = await FileCache.get(f"{username}_posts", default=None)
        if cached_posts is not None:
            value = [models_pb2.Message.FromString(v) for v in cached_posts]
            return value
        
    host = get_host(POST)
    channel = get_authenticated_channel(host, token)
    stub = MessageServiceStub(channel)
    request = GetMessagesRequest(user_id=username)

    try:
        response = stub.GetMessages(request)
        new_messages = []
        for message in response.messages:
            new_message = models_pb2.Message( message_id = message.message_id, user_id = message.user_id, content = message.content, timestamp = message.timestamp, is_repost = message.is_repost, original_message_id = message.original_message_id)
            new_messages.append(new_message)
        serialized_value = [v.SerializeToString() for v in new_messages]   
        await FileCache.set(f"{username}_posts", serialized_value)
        return new_messages
    except grpc.RpcError as error:
        logging.error(f"An error occurred fetching user posts: {error.code()}: {error.details()}")
        return None  
    
def post_message(username, content, token):
    host = get_host(POST)
    channel = get_authenticated_channel(host, token)
    stub = MessageServiceStub(channel)
    request = PostMessageRequest(user_id=username, content=content)

    try:
        response = stub.PostMessage(request)
        return True
    except grpc.RpcError as error:
        logging.error(f"An error occurred creating the post: {error.code()}: {error.details()}")
        return False
    
def repost_message(username, original_message_id, token):
    host = get_host(POST)
    channel = get_authenticated_channel(host ,token)
    stub = MessageServiceStub(channel)
    request = RepostMessageRequest(user_id=username, original_message_id=original_message_id)
    try:
        response = stub.RepostMessage(request)
        return True
    except grpc.RpcError as error:
        logging.error(f"An error occurred reposting: {error.code()}: {error.details()}")
        return False

    
 
