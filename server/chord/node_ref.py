import logging
import socket

from chord.constants import *
from chord.utils import getShaRepr
from config import PORT, SEPARATOR

class NodeRef:
    def __init__(self, ip: str, port: int = PORT):
        """
        Initializes a reference to a Chord node.

        Args:
            ip (str): IP address of the node.
            port (int): Port number of the node (default is the value from config).
        """
        self.id = getShaRepr(ip)  # Unique identifier for the node based on its IP address
        self.ip = ip
        self.port = port

    def process_operation(self, op: int, data: str = None) -> bytes:
        """
        Internal method to process a requested operation in the referenced node.

        Args:
            op (int): The operation code.
            data (str): The data to send (default is None).

        Returns:
            bytes: The response received from the node.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((self.ip, int(self.port)))
                s.sendall(f'{op}{SEPARATOR}{data}'.encode('utf-8'))
                return s.recv(1024)
        except Exception as e:
            logging.error(f"Error enviando dato a {self.ip}: {e}, operación: {op}, dato: {data}")
            return b''

    def find_predecessor(self, id: int) -> 'NodeRef':
        """
        Finds the predecessor of a given id.

        Args:
            id (int): The id to find the predecessor for.

        Returns:
            NodeRef: A reference to the predecessor node.
        """
        response = self.process_operation(FIND_ID_PREDECESSOR, str(id)).decode().split(SEPARATOR)
        return NodeRef(response[1], self.port)

    def find_successor(self, id: int) -> 'NodeRef':
        """
        Finds the successor of a given id.

        Args:
            id (int): The id to find the successor for.

        Returns:
            NodeRef: A reference to the successor node.
        """
        response = self.process_operation(FIND_ID_SUCCESSOR, str(id)).decode().split(SEPARATOR)
        return NodeRef(response[1], self.port)

    @property
    def pred(self) -> 'NodeRef':
        """
        Gets the predecessor of the current node.

        Returns:
            NodeRef: A reference to the predecessor node.
        """
        response = self.process_operation(GET_PREDECESSOR).decode().split(SEPARATOR)
        return NodeRef(response[1], self.port)

    @property
    def succ(self) -> 'NodeRef':
        """
        Gets the successor of the current node.

        Returns:
            NodeRef: A reference to the successor node.
        """
        response = self.process_operation(GET_SUCCESSOR).decode().split(SEPARATOR)
        return NodeRef(response[1], self.port)

    def closest_preceding_finger(self, id: int) -> 'NodeRef':
        """
        Finds the closest preceding finger for a given id.

        Args:
            id (int): The id to find the closest preceding finger for.

        Returns:
            NodeRef: A reference to the closest preceding finger node.
        """
        response = self.process_operation(CLOSEST_PRECEDING_FINGER, str(id)).decode().split(SEPARATOR)
        return NodeRef(response[1], self.port)