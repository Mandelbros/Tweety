import logging
import grpc
from concurrent import futures
import time 
from datetime import datetime, UTC
from proto.models_pb2 import Message
from proto.message_pb2 import PostMessageResponse, GetMessagesResponse, RepostMessageResponse
from proto.message_pb2_grpc import MessageServiceServicer, add_MessageServiceServicer_to_server
from repository.message import MessageRepository
from repository.auth import AuthRepository

class MessageService(MessageServiceServicer):
    def __init__(self, message_repository:MessageRepository, auth_repository: AuthRepository):
        self.message_repository = message_repository
        self.auth_repository = auth_repository

    def GetMessages(self, request, context):
        user_id = request.user_id

        if not self.auth_repository.load_user(user_id):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        messages, err = self.message_repository.load_messages_list(user_id)
        
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to load user posts")

        return GetMessagesResponse(messages=messages)

    def PostMessage(self, request, context):
        user_id = request.user_id

        content = request.content

        message_id = str(time.time_ns())
        iso_timestamp = datetime.now(UTC).isoformat()
        message = Message(message_id = message_id, user_id = user_id, content = content, timestamp = iso_timestamp, is_repost = False)

        err = self.message_repository.save_message(message)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to save post")

        err = self.message_repository.add_to_messages_list(message_id, user_id)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to add post to user list")

        return PostMessageResponse(success=True, message="Message posted successfully!")

    def RepostMessage(self, request, context):
        user_id = request.user_id
        
        messages, err = self.message_repository.load_messages_list(user_id)

        for message in messages:
            if message.original_message_id == request.original_message_id:
                return RepostMessageResponse(success=False, message="You already reposted this post")
            if message.message_id == request.original_message_id:  
                return RepostMessageResponse(success=False, message="This post is yours")

        original_message, err = self.message_repository.load_message(request.original_message_id)
        if err:
            context.abort(grpc.StatusCode.NOT_FOUND, "Original post not found")

        message_id = str(time.time_ns())
        iso_timestamp = datetime.now(UTC).isoformat()
        message = Message(message_id = message_id, user_id = user_id, content = original_message.content, timestamp = iso_timestamp, is_repost = True, original_message_id = original_message.message_id, original_message_user_id = original_message.user_id, original_message_timestamp = original_message.timestamp)

        err = self.message_repository.save_message(message)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to save repost")

        err = self.message_repository.add_to_messages_list(message_id, user_id)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to add repost to user list")

        return RepostMessageResponse(success=True, message="Message reposted successfully!")

    # def GetMessage(self, request, context):
    # def DeleteMessage(self, request, context):

def start_message_service(address, message_repository: MessageRepository, auth_repository: AuthRepository):
    logging.info("Post service started")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MessageServiceServicer_to_server(MessageService(message_repository,auth_repository), server)
    server.add_insecure_port(address)
    server.start()
    # print("Message service started on port 5003")
    server.wait_for_termination()