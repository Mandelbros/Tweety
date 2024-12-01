from concurrent import futures
import grpc
from server.proto.message_pb2 import PostMessageResponse, GetMessagesResponse, Message
from server.proto.message_pb2_grpc import MessageServiceServicer, add_MessageServiceServicer_to_server
import datetime
from server import shared_state 

class MessageService(MessageServiceServicer):
    def PostMessage(self, request, context):
        # Add the message to the in-memory storage
        timestamp = datetime.datetime.utcnow().isoformat()
        shared_state.messages.append({"username": request.username, "content": request.content, "timestamp": timestamp})
        return PostMessageResponse(success=True, message="Message posted successfully!")

    def GetMessages(self, request, context):
        # Return all messages or filter by username if provided
        if request.username:
            user_messages = [m for m in shared_state.messages if m["username"] == request.username]
        else:
            user_messages = shared_state.messages
        
        return GetMessagesResponse(messages=[
            Message(username=m["username"], content=m["content"], timestamp=m["timestamp"]) for m in user_messages
        ])

def start_message_service():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MessageServiceServicer_to_server(MessageService(), server)
    server.add_insecure_port('127.0.0.1:50053')
    server.start()
    print("Message service started or port 50053") ### loggin remove
    server.wait_for_termination()
