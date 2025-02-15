
import os
import grpc
from chord.node import Node 
from server.repository.utils import save, load
from server.proto.models_pb2 import Message, UserMessages

class MessageRepository:
    def __init__(self, node: Node) -> None:
        self.node = node

    def save_message(self, message):
        path = os.path.join("Message", message.message_id)
        err = save(self.node, message, path)

        if err:
            return grpc.StatusCode.INTERNAL("Failed to save post: {}".format(err))

        return None

    def load_message(self, message_id):
        path = os.path.join("Message", message_id)
        message, err = load(self.node, path, Message())

        if err == grpc.StatusCode.NOT_FOUND:
            return None, grpc.StatusCode.NOT_FOUND
        elif err:
            return None, grpc.StatusCode.INTERNAL

        return message, None

    def add_to_messages_list(self, message_id, username):
        path = os.path.join("Auth", username.lower(), "Messages")
        user_messages, err = load(self.node, path, UserMessages())
        list = []

        if not err:
            list = user_messages.messages_ids

        list.append(message_id)
        err = save(self.node, UserMessages(messages_ids = list), path)

        if err:
            return grpc.StatusCode.INTERNAL("Failed to save post to user: {}".format(err))

        return None

    def load_messages_list(self, username):
        path = os.path.join("Auth", username.lower(), "Messages")
        user_messages, err = load(self.node, path, UserMessages())
        list = []

        if err == grpc.StatusCode.NOT_FOUND:
            return list, None

        if err:
            return None, grpc.StatusCode.INTERNAL("Failed to load user posts: {}".format(err))

        for message_id in user_messages.messages_ids:
            message, err = self.load_message(message_id)
            if err:
                return None, err
            list.append(message)
        return list, None
