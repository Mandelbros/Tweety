import grpc
import logging
import base64
from config import MESSAGE
from cache import FileCache
from proto.message_pb2 import PostMessageRequest, GetMessagesRequest, RepostMessageRequest, GetMessageIDsRequest, GetMessageRequest, GetMessagesResponse, GetMessageIDsResponse, GetMessageResponse
from proto.message_pb2_grpc import MessageServiceStub 
from proto import models_pb2
from discoverer import get_host, get_authenticated_channel

async def get_messages(username, token, request=True):
    if not request:
        cached_posts = await FileCache.get(f"{username}_posts")
        if cached_posts is not None:
            value = [models_pb2.Message.FromString(base64.b64decode(v)) for v in cached_posts]
            response = GetMessagesResponse(messages = value)
            return response
        else:
            logging.info(f"Messages of user {username} not found in cache.")

    host = get_host(MESSAGE)
    channel = get_authenticated_channel(host, token)
    stub = MessageServiceStub(channel)
    request = GetMessagesRequest(user_id=username)

    try:
        response = stub.GetMessages(request)
        new_messages = []
        for message in response.messages:
            new_message = models_pb2.Message( message_id = message.message_id, user_id = message.user_id, content = message.content, timestamp = message.timestamp, is_repost = message.is_repost, original_message_id = message.original_message_id)
            new_messages.append(new_message)
        serialized_value = [base64.b64encode(v.SerializeToString()).decode('utf-8') for v in new_messages]   
        await FileCache.set(f"{username}_posts", serialized_value)              ###
        return response
    except grpc.RpcError as error:
        logging.error(f"An error occurred fetching user posts: {error.code()}: {error.details()}")
        
        logging.info(f"Recurring to cached user posts")
        cached_posts = await FileCache.get(f"{username}_posts")
        if cached_posts is not None:
            value = [models_pb2.Message.FromString(base64.b64decode(v)) for v in cached_posts]
            response = GetMessagesResponse(messages = value)
            return response
        else:
            logging.info(f"Messages of user {username} not found in cache.")
            return None  
    
async def get_message_ids(username, token, request=True):
    if not request:
        cached_post_ids = await FileCache.get(f"{username}_post_ids")
        if cached_post_ids is not None:
            value = [base64.b64decode(v) for v in cached_post_ids]
            response = GetMessageIDsResponse(message_ids = value)
            return response
        else:
            logging.info(f"Message IDs of user {username} not found in cache.")

    host = get_host(MESSAGE)
    channel = get_authenticated_channel(host, token)
    stub = MessageServiceStub(channel)
    request = GetMessageIDsRequest(user_id = username)

    try:
        response = stub.GetMessageIDs(request)
        serialized_value = [base64.b64encode(v.encode('utf-8')).decode('utf-8') for v in response.message_ids]
        await FileCache.set(f"{username}_post_ids", serialized_value)
        return response
    except grpc.RpcError as error:
        logging.error(f"An error occurred fetching user post IDs: {error.code()}: {error.details()}")

        logging.info(f"Recurring to cached user post IDs")
        cached_post_ids = await FileCache.get(f"{username}_post_ids")
        if cached_post_ids is not None:
            value = [base64.b64decode(v) for v in cached_post_ids]
            response = GetMessageIDsResponse(message_ids = value)
            return response
        else:
            logging.info(f"Message IDs of user {username} not found in cache.")
            return None
    
async def get_message(message_id, token, request=False):
    if not request:
        cached_post = await FileCache.get(f"message_{message_id}")
        if cached_post is not None:
            value = models_pb2.Message.FromString(base64.b64decode(cached_post))
            response = GetMessageResponse(message = value)
            return response
        else:
            logging.info(f"Message {message_id} not found in cache.")
    
    host = get_host(MESSAGE)
    channel = get_authenticated_channel(host, token)
    stub = MessageServiceStub(channel)
    request = GetMessageRequest(message_id=message_id)

    try:
        response = stub.GetMessage(request)
        serialized_value = base64.b64encode(response.message.SerializeToString()).decode('utf-8')  
        await FileCache.set(f"messages/message_{message_id}", serialized_value)
        return response
    except grpc.RpcError as error:
        logging.error(f"An error occurred fetching post: {error.code()}: {error.details()}")

        logging.info(f"Recurring to cached post")
        cached_post = await FileCache.get(f"message_{message_id}")
        if cached_post is not None:
            value = models_pb2.Message.FromString(base64.b64decode(cached_post))
            response = GetMessageResponse(message = value)
            return response
        else:
            logging.info(f"Message {message_id} not found in cache.")
            return None  
    
def post_message(username, content, token):
    host = get_host(MESSAGE)
    channel = get_authenticated_channel(host, token)
    stub = MessageServiceStub(channel)
    request = PostMessageRequest(user_id=username, content=content)

    try:
        response = stub.PostMessage(request)
        return response
    except grpc.RpcError as error:
        logging.error(f"An error occurred creating the post: {error.code()}: {error.details()}")
        return False
    
def repost_message(username, original_message_id, token):
    host = get_host(MESSAGE)
    channel = get_authenticated_channel(host ,token)
    stub = MessageServiceStub(channel)
    request = RepostMessageRequest(user_id=username, original_message_id=original_message_id)
    try:
        response = stub.RepostMessage(request)
        return response
    except grpc.RpcError as error:
        logging.error(f"An error occurred reposting: {error.code()}: {error.details()}")
        return False

    
 
