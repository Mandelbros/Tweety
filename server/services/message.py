from concurrent import futures
import grpc
from server.proto.models_pb2 import Message
from server.proto.message_pb2 import PostMessageResponse, GetMessagesResponse, RepostMessageResponse
from server.proto.message_pb2_grpc import MessageServiceServicer, add_MessageServiceServicer_to_server
import datetime, time
from server import shared_state

class MessageService(MessageServiceServicer):
    def PostMessage(self, request, context):
        # Add the message to the in-memory storage
        timestamp = datetime.datetime.utcnow().isoformat()
        message_id = str(time.time_ns())
        shared_state.messages.append({
            "message_id": message_id,
            "username": request.username,
            "content": request.content,
            "timestamp": timestamp,
            "is_repost": False,
            "original_message_id": None,
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
                message_id=m["message_id"],
                username=m["username"],
                content=m["content"],
                timestamp=m["timestamp"],
                is_repost=m["is_repost"],
                original_message_id=m["original_message_id"] or ""
            ) for m in user_messages
        ])

    def RepostMessage(self, request, context):
        # Validate the original message index
        if request.original_message_index < 0 or request.original_message_index >= len(shared_state.messages):
            return RepostMessageResponse(success=False, message="Invalid message index.")
        
        original_message = shared_state.messages[request.original_message_index]
        
        # Add the reposted message to the shared state
        timestamp = datetime.datetime.utcnow().isoformat()
        message_id = str(time.time_ns())

        shared_state.messages.append({
            "message_id": message_id,
            "username": request.username,
            "content": original_message["content"],
            "timestamp": timestamp,
            "is_repost": True,
            "original_message_id": original_message["message_id"],
        })
        return RepostMessageResponse(success=True, message="Message reposted successfully!")

def start_message_service():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MessageServiceServicer_to_server(MessageService(), server)
    # server.add_insecure_port('0.0.0.0:50053')
    server.add_insecure_port('10.0.11.10:5003')
    server.start()
    print("Message service started on port 5003")
    server.wait_for_termination()
