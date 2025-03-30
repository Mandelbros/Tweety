import os
import grpc
from chord.node import Node 
from repository.utils import save, load
from proto.models_pb2 import Message, UserMessages
import logging

class MessageRepository:
    def __init__(self, node: Node) -> None:
        self.node = node

    def save_message(self, message):
        path = os.path.join("Message", message.message_id)
        err = save(self.node, message, path)

        if err:
            logging.error("Failed to save post: {}".format(err))
            return grpc.StatusCode.INTERNAL

        return None

    def load_message(self, message_id):
        path = os.path.join("Message", str(message_id))
        message, err = load(self.node, path, Message())

        if err == grpc.StatusCode.NOT_FOUND:
            return None, grpc.StatusCode.NOT_FOUND
        elif err:
            return None, grpc.StatusCode.INTERNAL

        return message, None

    def add_to_messages_list(self, message_id, username):
        path = os.path.join("User", username.lower(), "Messages")
        user_messages, err = load(self.node, path, UserMessages())
        list = []

        if not err:
            list = user_messages.message_ids

        list.append(message_id)
        err = save(self.node, UserMessages(message_ids = list), path)

        if err:
            logging.error("Failed to save post to user: {}".format(err))
            return grpc.StatusCode.INTERNAL

        return None

    def load_messages_list(self, username):
        path = os.path.join("User", username.lower(), "Messages")
        user_messages, err = load(self.node, path, UserMessages())
        list = []

        if err == grpc.StatusCode.NOT_FOUND:
            return list, None

        if err:
            logging.error("Failed to load user posts: {}".format(err))
            return grpc.StatusCode.INTERNAL, None

        for message_id in user_messages.message_ids:
            message, err = self.load_message(message_id)
            if err:
                return None, err
            list.append(message)
        return list, None
    
    def load_message_ids_list(self, username):
        path = os.path.join("User", username.lower(), "Messages")
        user_messages, err = load(self.node, path, UserMessages())
        list = []

        if err == grpc.StatusCode.NOT_FOUND:
            return list, None

        if err:
            logging.error("Failed to load user post IDs: {}".format(err))
            return grpc.StatusCode.INTERNAL, None
        
        for message_id in user_messages.message_ids:
            list.append(message_id)
        return list, None