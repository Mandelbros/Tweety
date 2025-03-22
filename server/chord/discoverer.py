import logging
import socket
import time

from chord.node_ref import NodeRef
from chord.constants import ARE_YOU, EMPTY, YES_IM
from config import SEPARATOR, MULTICAST_GROUP, MULTICAST_PORT
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
        Multicast announcement to discover a chord ring.
        The node sends a message to find any existing ring in the network.

        Returns:
            tuple: The IP of the discovered node and leader, or EMPTY values and error if no discovery occurs.
        """
        import struct

        logging.info('Enviando multicast para descubrir un anillo de Chord existente...')
        timeout = 5  # Set a timeout for discovery attempts
        multicast_addr = (MULTICAST_GROUP, MULTICAST_PORT)

        try:
            # Create a UDP socket
            conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            ttl = struct.pack('b', 1)
            conn.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        except Exception as e:
            logging.error(f"Error configurando socket multicast: {e}")
            return EMPTY, EMPTY, e

        # Compose the multicast message with the node's ID
        message = f"{ARE_YOU}{SEPARATOR}{self.node.id}".encode()
        try:
            conn.sendto(message, multicast_addr)
        except Exception as e:
            logging.error(f"Error enviando mensaje multicast: {e}")
            return EMPTY, EMPTY, e

        buffer = bytearray(1024)
        conn.settimeout(2)

        for _ in range(timeout):
            try:
                nn, addr = conn.recvfrom_into(buffer)
                res = buffer[:nn].decode().split(SEPARATOR)
                message = res[0]

                if message == YES_IM and len(res) == 2:
                    ip = addr[0]
                    leader_ip = res[1]
                    logging.info(f"Anillo de Chord descubierto en {ip}. IP del líder: {leader_ip}")
                    return ip, leader_ip, None
            except socket.timeout:
                continue
            except Exception as e:
                logging.error(f"Error recibiendo mensaje: {e}")
                return EMPTY, EMPTY, e

        logging.info("Ningún anillo de Chord descubierto.")
        return EMPTY, EMPTY, None

    def listen_for_announcements(self):
        """
        Listens for multicast announcements from other nodes that are looking to join
        or discover the chord ring.
        """
        import struct

        try:
            logging.info("Configurando socket multicast listener...")

            conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            conn.bind(('', MULTICAST_PORT))

            # Join the multicast group
            group = socket.inet_aton(MULTICAST_GROUP)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            conn.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            logging.info(f"Unido al grupo multicast {MULTICAST_GROUP} en el puerto {MULTICAST_PORT}")
        except Exception as e:
            logging.error(f"Error configurando socket multicast listener: {e}")
            return

        buffer = bytearray(1024)

        while True:
            try:
                # Espera el mensaje multicast
                logging.debug("Esperando mensaje multicast...")
                nn, client_addr = conn.recvfrom_into(buffer)

                # Verifica si se ha recibido algo
                if nn == 0:
                    logging.debug("No se recibió ningún mensaje, continuando...")
                    continue

                logging.info(f"Mensaje recibido de {client_addr} ({nn} bytes)")

            except Exception as e:
                logging.error(f"Error leyendo del buffer: {e}")
                continue

            try:
                # Revisa el ID del líder
                with self.elector.leader_lock:
                    leader_id = self.elector.leader.id

                logging.debug(f"Líder actual: {leader_id}, Nodo actual: {self.node.id}")

                if leader_id != self.node.id:
                    logging.debug("Este nodo no es el líder, ignorando mensaje...")
                    continue  # Ignorar si no es el líder

                res = buffer[:nn].decode().split(SEPARATOR)

                if len(res) != 2:
                    logging.debug(f"Mensaje mal formado, se esperaban 2 partes pero se recibió: {len(res)}")
                    continue

                message, id_str = res[0], res[1]

                try:
                    id = int(id_str)
                except ValueError:
                    logging.debug(f"ID inválido recibido: {id_str}, ignorando mensaje...")
                    continue

                if id == self.node.id:
                    logging.debug(f"Mensaje recibido del propio nodo (ID: {self.node.id}), ignorando...")
                    continue  # Ignorar los mensajes propios

                logging.info(f"Mensaje recibido: {message} con ID: {id} de {client_addr}")

                if message == ARE_YOU:
                    with self.elector.leader_lock:
                        leader = self.elector.leader

                    # Enviar la respuesta al mismo grupo multicast
                    response = f"{YES_IM}{SEPARATOR}{leader.ip}".encode()
                    logging.info(f"Enviando respuesta a {MULTICAST_GROUP} ({MULTICAST_PORT}) con IP del líder: {leader.ip}")
                    conn.sendto(response, (MULTICAST_GROUP, MULTICAST_PORT))

            except Exception as e:
                logging.error(f"Error procesando el mensaje: {e}")

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
                            logging.error(f'Error en multicast: {error}')
                    else:
                        leader = NodeRef(leader_ip)
                        if leader.id > self.node.id:
                            if not self.join(node_ip, leader_ip):
                                logging.error(f'Error uniendo nodo {node_ip}')
            except Exception as e:
                logging.error(f'Error en proceso de descubrimiento y unión: {e}')
            # Sleep for 60 seconds before retrying
            time.sleep(60)
