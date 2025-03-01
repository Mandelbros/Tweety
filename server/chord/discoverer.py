import logging
import socket
import time

from chord.node_ref import NodeRef
from chord.constants import ARE_YOU, EMPTY, YES_IM
from config import BROADCAST_LISTEN_PORT, BROADCAST_REQUEST_PORT, SEPARATOR
from chord.elector import Elector
from chord.finger_table import FingerTable

class Discoverer:
    """
    A class to handle the discovery and joining of a Chord ring. The class provides
    methods for discovering an existing chord ring, joining it, or creating a new ring.
    
    Attributes:
        node: The node that is trying to join or create a chord ring.
        succ_lock: A lock to synchronize access to the successors of the node.
        pred_lock: A lock to synchronize access to the predecessors of the node.
        elector: The Elector object responsible for leader election.
        finger: The FingerTable object associated with the node.
    """
    
    def __init__(self, node, succ_lock, pred_lock, elector: Elector, finger: FingerTable) -> None:
        """
        Initializes the Discoverer with the necessary components for chord ring discovery.
        
        Args:
            node: The node trying to discover or join a chord ring.
            succ_lock: Lock for accessing the node's successors.
            pred_lock: Lock for accessing the node's predecessors.
            elector: The Elector object responsible for leader election.
            finger: The FingerTable object of the node.
        """
        self.node = node
        self.succ_lock = succ_lock
        self.pred_lock = pred_lock
        self.elector = elector
        self.finger = finger

    def join(self, node_ip, leader_ip):
        """
        Joins the chord ring by connecting to a specified node and leader.

        Args:
            node_ip (str): The IP address of the node to connect to.
            leader_ip (str): The IP address of the leader of the chord ring.

        Returns:
            bool: True if successfully joined the ring, False otherwise.
        """
        node = NodeRef(node_ip)
        leader = NodeRef(leader_ip)
        try:
            with self.succ_lock and self.pred_lock:
                # Set the node's predecessor to itself (index 0 in predecessors list)
                self.node.predecessors.set(0, self.node.ref)
                # Clear the current successors and set the first successor as the node found by find_successor
                self.node.successors.clear()
                self.node.successors.set(0, node.find_successor(self.node.id))
                succ: NodeRef = self.node.successors.get(0)

                # Update the finger table with the new successor at index 0
                with self.finger.finger_lock:
                    self.finger.finger[0] = succ

                # Set the leader in the elector as the one received
                with self.elector.leader_lock:
                    self.elector.leader = leader
                
                # Notify the new successor about this node
                succ.notify(self.node.ref)
                
                logging.info(f'Unido exitosamente al anillo de Chord a través del nodo {node.ip}.')
                return True
        except Exception as e:
            # Log any errors encountered while trying to join the chord ring
            logging.error(f'Error mientras se unía al anillo de Chord: {e}')
            return False

    def send_announcement(self):
        """
        Broadcasts an announcement to discover a chord ring. The node sends a message
        to find any existing ring in the network.

        Returns:
            tuple: The IP of the discovered node and leader, or EMPTY values and error if no discovery occurs.
        """
        logging.info('Broadcasting para descubrir un anillo de Chord existente...')
        timeout = 5  # Set a timeout for discovery attempts

        broadcast_addr = ('<broadcast>', int(BROADCAST_LISTEN_PORT))

        try:
            # Create a socket for broadcasting
            conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            conn.bind(('', int(BROADCAST_REQUEST_PORT)))
        except Exception as e:
            logging.error(f"Error montando el socket de broadcast: {e}")
            return EMPTY, EMPTY, e

        # Compose the broadcast message with the node's ID
        message = f"{ARE_YOU}{SEPARATOR}{self.node.id}".encode()
        conn.sendto(message, broadcast_addr)

        buffer = bytearray(1024)  # Buffer to store incoming messages
        conn.settimeout(2)  # Set a timeout for receiving responses

        # Attempt to receive responses for the set timeout duration
        for _ in range(timeout):
            try:
                nn, addr = conn.recvfrom_into(buffer)  # Receive response from any node
                res = buffer[:nn].decode().split(SEPARATOR)
                message = res[0]

                # If the response is valid, return the IP and leader information
                if message == YES_IM and len(res) == 2:
                    ip = addr[0]
                    leader_ip = res[1]
                    logging.info(f"Anillo de Chord descubierto en {ip}. IP del leader: {leader_ip}")
                    return ip, leader_ip, None
            except socket.timeout:
                continue  # Retry on timeout
            except Exception as e:
                logging.error(f"Error recibiendo mensaje: {e}")
                return EMPTY, EMPTY, e

        logging.info("Ningún anillo de Chord descubierto.")
        return EMPTY, EMPTY, None

    def listen_for_announcements(self):
        """
        Listens for broadcast announcements from other nodes that are looking to join
        or discover the chord ring.

        This function waits for incoming messages and responds with the current node's leader.
        """
        try:
            # Create a socket to listen for announcements
            conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            conn.bind(('', BROADCAST_LISTEN_PORT))
        except Exception as e:
            logging.error(f"Error corriendo servidor UDP: {e}")
            return

        buffer = bytearray(1024)  # Buffer to store received messages

        while True:
            try:
                # Wait for incoming messages
                nn, client_addr = conn.recvfrom_into(buffer)
            except Exception as e:
                logging.error(f"Error leyendo del buffer: {e}")
                continue

            with self.elector.leader_lock:
                leader_id = self.elector.leader.id

            if leader_id != self.node.id:
                continue  # Ignore messages if this node is not the leader

            res = buffer[:nn].decode().split(SEPARATOR)

            if len(res) != 2:
                continue  # Skip invalid messages

            message = res[0]
            id = int(res[1])

            if id == self.node.id:
                continue  # Ignore messages from itself

            logging.info(f"Mensaje recibido de {client_addr}")

            if message == ARE_YOU:
                with self.elector.leader_lock:
                    leader = self.elector.leader

                # Respond with YES_IM and the leader's IP address
                response = f"{YES_IM}{SEPARATOR}{leader.ip}".encode()
                conn.sendto(response, client_addr)

    def create_ring(self):
        """
        Creates a new chord ring by initializing the node's predecessor, successor, and leader.
        This is used when the node is the first in the ring.
        """
        logging.info('Creando un nuevo anillo de Chord...')
        with self.pred_lock:
            self.node.predecessors.set(0, self.node.ref)
        with self.succ_lock:
            self.node.successors.set(0, self.node.ref)
        with self.elector.leader_lock:
            self.elector.leader = self.node.ref

    def create_ring_or_join(self):
        """
        Attempts to either join an existing chord ring or create a new ring if none is discovered.
        """
        node_ip, leader_ip, error = self.send_announcement()

        if not error and node_ip != EMPTY:
            # If a node and leader are found, try joining the ring
            if not self.join(node_ip, leader_ip):
                self.create_ring()
            return 
        
        # If no chord ring is found, create a new ring
        self.create_ring()

    def discover_and_join(self):
        """
        Periodically checks if the node is the leader or isolated, and attempts to discover
        or join a chord ring.

        This function is typically used in a separate thread to keep the node continuously
        updated about its status in the chord ring.
        """
        while not self.node.shutdown_event.is_set():
            try:
                with self.elector.leader_lock:
                    leader_id = self.elector.leader.id
                with self.node.succ_lock:
                    succ: NodeRef = self.node.successors.get(0)
                with self.node.pred_lock:
                    pred: NodeRef = self.node.predecessors.get(0)
                alone = succ.id == pred.id and succ.id == self.node.id

                # Check if this node is the leader or isolated
                if leader_id == self.node.id or alone:
                    # If the node is isolated, attempt to discover a chord ring
                    node_ip, leader_ip, error = self.send_announcement()
                    if error or node_ip == EMPTY:
                        if error:
                            logging.error(f'Error en broadcast: {error}')
                    else:
                        leader = NodeRef(leader_ip)
                        if leader.id > self.node.id:
                            if not self.join(node_ip, leader_ip):
                                logging.error(f'Error uniendo nodo {node_ip}')
            except Exception as e:
                logging.error(f'Error en proceso de descubrimiento y unión: {e}')
            # Sleep for 60 seconds before retrying
            time.sleep(60)
