import logging
import threading
import time
from chord.timer import Timer
from chord.node_ref import NodeRef
from config import SEPARATOR
from chord.constants import CHECK_LEADER_FREQ, CHECK_FOR_ELECTION_FREQ

class Elector:
    """
    The Elector class is responsible for managing leader election and maintaining
    communication with the current leader in the distributed system.
    """
    def __init__(self, node, timer: Timer) -> None:
        """
        Initializes the Elector object with the node reference and timer instance.

        Args:
            node: The node to which this elector belongs.
            timer: The Timer object used to track time for the election process.
        """
        self.node = node
        self.leader: NodeRef = None  # The reference to the current leader
        self.leader_lock = threading.RLock()  # Lock for thread-safe access to leader
        self.timer = timer

    def ping_leader(self, id: int, time: int):
        """
        Pings the leader to synchronize time between the nodes.
        
        Args:
            id: The ID of the node making the request.
            time: The current time of the node.
        
        Returns:
            int: The updated time after the leader responds.
        """
        with self.timer.time_lock:
            # Update the timer with the current time from the node
            self.timer.node_timers[id] = time
            self.timer.time_counter = self.timer.berkeley_algorithm()  # Sync the time using Berkeley algorithm
            self.timer.node_timers[self.node.id] = self.timer.time_counter

            logging.debug(f"Nodo {self.node.id} sincronizó su tiempo con el líder {self.leader.id} como {self.timer.time_counter}")
            return self.timer.time_counter

    def check_leader(self):
        """
        Periodically checks if the leader is still alive by pinging it. 
        If the leader fails to respond, an election is triggered.
        """
        while not self.node.shutdown_event.is_set():
            with self.leader_lock:
                if self.leader and self.leader.id != self.node.id:
                    logging.info(f"Revisando líder con ID: {self.leader.id}")

                    with self.timer.time_lock:
                        current_time = self.timer.time_counter

                    try:
                        # Ping the leader and update the time
                        time_response = self.leader.ping_leader(self.node.id, current_time)
                        with self.timer.time_lock:
                            self.timer.time_counter = time_response
                            self.timer.node_timers[self.node.id] = time_response
                    except Exception as e:
                        logging.error(f"Líder {self.leader.id} falló: {e}")
                        # Trigger election if the leader fails
                        self.call_for_election()
            # Sleep for CHECK_LEADER_FREQ seconds before checking again
            time.sleep(CHECK_LEADER_FREQ)

    def call_for_election(self):
        """
        Calls for an election by trying to contact the node's successor. If successful,
        the successor participates in the election process.
        If no valid successor is found, the current node becomes the leader.
        """
        with self.node.succ_lock:
            succ: NodeRef = self.node.successors.get(0)

        if self.node.id == succ.id:
            with self.leader_lock:
                self.leader = self.node.ref  # Node becomes the leader if it's alone
            logging.info(f"Nodo {self.node.id} es el líder ahora")
            return
        
        logging.info("Proceso de elección iniciado")
        ok = succ.ping()
        if not ok:
            # If the successor is unreachable, the current node becomes the leader
            with self.leader_lock:
                self.leader = self.node.ref
            logging.error(f"Fallo al conectar al sucesor {succ.id}")
            return
        
        try:
            # Ask the successor to perform the election
            self.leader = succ.election(self.node.id, self.node.ip, self.node.port)
            logging.info(f"Nuevo líder electo: {self.leader.id}")
        except Exception as e:
            # If election fails, the current node becomes the leader
            with self.leader_lock:
                self.leader = self.node.ref
            logging.error(f"Elección fallida: {e}")

    def election(self, first_id, leader_ip, leader_port):
        """
        Executes the election process by passing the election request to the successor nodes.
        Returns the leader's IP and port upon successful election.

        Args:
            first_id: The ID of the first node that started the election process.
            leader_ip: The IP address of the candidate leader.
            leader_port: The port of the candidate leader.

        Returns:
            str: The IP and port of the elected leader, or None if election fails.
        """
        new_leader = NodeRef(leader_ip, leader_port)

        if self.node.id > new_leader.id:
            new_leader = self.node.ref  # The current node wins if it has a higher ID

        with self.node.succ_lock:
            succ: NodeRef = self.node.successors.get(0)

        if succ.id == self.node.id or succ.id == first_id:
            # If the successor is the node itself or the first node, it means the election is complete
            with self.leader_lock:
                self.leader = new_leader

            logging.info(f"Líder electo: {new_leader.id} en {new_leader.ip}:{new_leader.port}")
            return f'{new_leader.ip}{SEPARATOR}{new_leader.port}'

        ok = succ.ping()
        if not ok:
            logging.info('Fallo al conectar al sucesor, elección de líder fallida.')
            return None

        try:
            # Continue the election by passing the request to the successor
            new_leader = succ.election(first_id, new_leader.ip, new_leader.port)
        except Exception as e:
            logging.info(f"Elección fallida: {e}")
            return None

        with self.leader_lock:
            self.leader = new_leader

        logging.info(f"Líder electo: {new_leader.id} en {new_leader.ip}:{new_leader.port}")
        return f'{new_leader.ip}{SEPARATOR}{new_leader.port}'
    
    def check_for_election(self):
        """
        This thread is responsible for periodically checking if an election is needed.
        If the current node is the leader, it triggers the election process.
        """
        logging.info("Hilo de Elección iniciado")
        while not self.node.shutdown_event.is_set():
            try:
                with self.leader_lock:
                    leader_id = self.leader.id
                if leader_id == self.node.id:
                    self.call_for_election()
            except Exception as e:
                logging.error(f'Error en Hilo de Elección: {e}')
            # Sleep for CHECK_FOR_ELECTION_FREQ seconds before the next election check
            time.sleep(CHECK_FOR_ELECTION_FREQ)
