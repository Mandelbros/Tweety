from concurrent import futures
import grpc
from server.proto.message_pb2 import PostMessageResponse, GetMessagesResponse, RepostMessageResponse, Message
from server.proto.message_pb2_grpc import MessageServiceServicer, add_MessageServiceServicer_to_server
import datetime
from server import shared_state

class MessageService(MessageServiceServicer):
    def PostMessage(self, request, context):
        # Add the message to the in-memory storage
        timestamp = datetime.datetime.utcnow().isoformat()
        shared_state.messages.append({
            "username": request.username,
            "content": request.content,
            "timestamp": timestamp,
            "is_repost": False,
            "original_username": None,
        })
        return PostMessageResponse(success=True, message="Message posted successfully!")

    def GetMessages(self, request, context):
        # Return all messages or filter by username if provided
        if request.username:
            user_messages = [m for m in shared_state.messages if m["username"] == request.username]
        else:
            user_messages = shared_state.messages

        return GetMessagesResponse(messages=[
            Message(
                username=m["username"],
                content=m["content"],
                timestamp=m["timestamp"],
                is_repost=m["is_repost"],
                original_username=m["original_username"] or ""
            ) for m in user_messages
        ])

    def RepostMessage(self, request, context):
        # Validate the original message index
        if request.original_message_index < 0 or request.original_message_index >= len(shared_state.messages):
            return RepostMessageResponse(success=False, message="Invalid message index.")
        
        original_message = shared_state.messages[request.original_message_index]
        
        # Add the reposted message to the shared state
        timestamp = datetime.datetime.utcnow().isoformat()
        shared_state.messages.append({
            "username": request.username,
            "content": original_message["content"],
            "timestamp": timestamp,
            "is_repost": True,
            "original_username": original_message["username"],
        })
        return RepostMessageResponse(success=True, message="Message reposted successfully!")

def start_message_service():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MessageServiceServicer_to_server(MessageService(), server)
    server.add_insecure_port('0.0.0.0:50053')
    server.start()
    print("Message service started on port 50053")
    server.wait_for_termination()
