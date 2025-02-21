import logging
import grpc
from concurrent import futures
import time 
from server.proto.models_pb2 import Message
from server.proto.message_pb2 import PostMessageResponse, GetMessagesResponse, RepostMessageResponse
from server.proto.message_pb2_grpc import MessageServiceServicer, add_MessageServiceServicer_to_server
from server.repository.message import MessageRepository
from server.repository.auth import AuthRepository

class MessageService(MessageServiceServicer):
    def __init__(self, auth_repository, message_repository):
        self.auth_repository = auth_repository
        self.message_repository = message_repository

    def PostMessage(self, request, context):
        user_id = request.user_id

        content = request.content

        message_id = str(time.time_ns())
        message = Message(message_id = message_id, user_id = user_id, content = content, timestamp = int(time.time()))

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
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "User already reposted this post")
            if message.message_id == request.original_message_id:  
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "This post is yours")

        original_message, err = self.message_repository.load_message(request.original_message_id)
        if err:
            context.abort(grpc.StatusCode.NOT_FOUND, "Original post not found")

        message_id = str(time.time_ns())
        message = Message(message_id = message_id, user_id = user_id, content = original_message.content, timestamp = int(time.time()), original_post_id = original_message.message_id)

        err = self.message_repository.save_message(message)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to save repost")

        err = self.message_repository.add_to_messages_list(message_id, user_id)
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to add repost to user list")

        return RepostMessageResponse(success=True, message="Message reposted successfully!")

    def GetMessages(self, request, context):
        user_id = request.user_id

        if not self.auth_repository.load_user(user_id):
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        messages, err = self.message_repository.load_messages_list(user_id)
        
        if err:
            context.abort(grpc.StatusCode.INTERNAL, "Failed to load user posts")

        return GetMessagesResponse(messages=messages)

def start_message_service(message_repository: MessageRepository, auth_repository: AuthRepository):
    logging.info("Post service started")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MessageServiceServicer_to_server(MessageService(message_repository,auth_repository), server)

    # server.add_insecure_port('0.0.0.0:50053')
    server.add_insecure_port('10.0.11.10:5003')
    server.start()
    # print("Message service started on port 5003")
    server.wait_for_termination()