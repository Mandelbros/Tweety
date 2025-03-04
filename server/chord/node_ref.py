import logging
import socket
from typing import List, Tuple

from chord.constants import *
from chord.utils import getShaRepr
from chord.storage import Data
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
    
    def notify(self, node: 'NodeRef'):
        """
        Notifies the current node about the presence of another node.

        Args:
            node (NodeRef): The node to notify.
        """
        self.process_operation(NOTIFY, f'{node.ip}{SEPARATOR}{node.port}')

    def get_successor_and_notify(self, index, ip) -> 'NodeRef':
        """
        Retrieves the successor node and notifies it.

        Args:
            index (int): The index of the node.
            ip (str): The IP address of the node.

        Returns:
            NodeRef: A reference to the successor node.
        """
        response = self.process_operation(GET_SUCCESSOR_AND_NOTIFY, f'{index}{SEPARATOR}{ip}').decode().split(SEPARATOR)
        return NodeRef(response[1], self.port)
    
    def ping(self) -> bool:
        """
        Pings the current node to check if it is alive.

        Returns:
            bool: True if the node is alive, False otherwise.
        """
        response = self.process_operation(PING).decode()
        return response == ALIVE
    
    def ping_leader(self, id: int, time: int):
        """
        Pings the leader node.

        Args:
            id (int): The id of the node sending the ping.
            time (int): The time of the ping.

        Returns:
            int: The response from the leader node.
        """
        response = self.process_operation(PING_LEADER, f'{id}{SEPARATOR}{time}').decode()
        return int(response)

    def election(self, first_id: int, leader_ip: int, leader_port: int) -> 'NodeRef':
        """
        Performs an election to determine the leader node.

        Args:
            first_id (int): The id of the first node.
            leader_ip (int): The IP address of the leader node.
            leader_port (int): The port of the leader node.

        Returns:
            NodeRef: A reference to the newly elected leader node.
        """
        response = self.process_operation(ELECTION, f'{first_id}{SEPARATOR}{leader_ip}{SEPARATOR}{leader_port}').decode().split(SEPARATOR)
        return NodeRef(response[0], response[1])
    
    def set_partition(self, dict: str, version: str, remove: str) -> bool:
        """
        Sets the partition on the current node.

        Args:
            dict (str): The dictionary for the partition.
            version (str): The version of the partition.
            remove (str): The key to remove.

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        response = self.process_operation(SET_PARTITION, f'{dict}{SEPARATOR}{version}{SEPARATOR}{remove}').decode()
        return False if response == '' else int(response) == TRUE

    def resolve_data(self, dict: str, version: str, remove: str) -> Tuple[List[str], bool]:
        """
        Resolves data based on the given dictionary, version, and remove flags.

        Args:
            dict (str): The dictionary for the data.
            version (str): The version of the data.
            remove (str): The key to remove.

        Returns:
            Tuple[List[str], bool]: A tuple containing the list of resolved data and a flag indicating whether there were multiple entries.
        """
        response = self.process_operation(RESOLVE_DATA, f'{dict}{SEPARATOR}{version}{SEPARATOR}{remove}').decode().split(SEPARATOR)
        return response, len(response) > 1
    
    def retrieve_key(self, key: str) -> Data:
        """
        Retrieves the value for a given key from the current node.

        Args:
            key (str): The key to retrieve.

        Returns:
            Data: The data associated with the key.
        """
        response = self.process_operation(RETRIEVE_KEY, key).decode().split(SEPARATOR)
        return Data(response[0], int(response[1]))

    def store_key(self, key: str, value: str, version: int, rep: bool = False) -> bool:
        """
        Stores a key-value pair in the current node.

        Args:
            key (str): The key to store.
            value (str): The value to store.
            version (int): The version of the key-value pair.
            rep (bool): Whether the key-value pair is replicated (default is False).

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        response = self.process_operation(STORE_KEY, f'{key}{SEPARATOR}{value}{SEPARATOR}{version}{SEPARATOR}{TRUE if rep else FALSE}').decode()
        return False if response == '' else int(response) == TRUE

    def delete_key(self, key: str, time: int, rep: bool = False) -> bool: 
        """
        Deletes a key-value pair from the current node.

        Args:
            key (str): The key to delete.
            time (int): The timestamp of the deletion.
            rep (bool): Whether the key-value pair is replicated (default is False).

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        response = self.process_operation(DELETE_KEY, f'{key}{SEPARATOR}{time}{SEPARATOR}{TRUE if rep else FALSE}').decode()
        return False if response == '' else int(response) == TRUE
