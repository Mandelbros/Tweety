import logging
import threading
import socket
import time

from chord.utils import  getShaRepr
from chord.node_ref import NodeRef
from chord.bounded_list import BoundedList
from chord.finger_table import FingerTable
from chord.constants import *
from chord.utils import is_in_interval
from config import SEPARATOR

class Node:
    def __init__(self, ip: str, port: int = 8001, m: int = 160, c: int = 3):
        """
        Initializes a new Chord node with given parameters.

        Args:
            ip (str): The IP address of the node.
            port (int): The port the node will listen on.
            m (int): The number of bits for the ID space.
            c (int): The number of successors and predecessors to maintain.
        """
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = NodeRef(self.ip, self.port)
        self.c = c

        # Successor and predecessor lists with locking mechanisms for thread safety
        self.successors = BoundedList[NodeRef](c, self.ref)
        self.succ_lock = threading.RLock()

        self.predecessors = BoundedList[NodeRef](c, self.ref)
        self.pred_lock = threading.RLock()

        self.shutdown_event = threading.Event()

        threading.Thread(target=self.start_server, daemon=True).start()

        self.finger = FingerTable(self, m)

        # Start the thread for maintaining the finger table
        threading.Thread(target=self.finger.fix_fingers, daemon=True).start()
        threading.Thread(target=self.stabilize, daemon=True).start()
        threading.Thread(target=self.check_predecessor, daemon=True).start()
        threading.Thread(target=self.check_successor, daemon=True).start()
        threading.Thread(target=self.fix_successors, daemon=True).start()
        
    def get_key(self, key: str) -> str:
        logging.info(f'Get key {key}')

        return ''

    def set_key(self, key: str, value: str) -> bool:
        logging.info(f'Set key {key} with value {value}')

        return 0

    def remove_key(self, key: str) -> bool:
        logging.info(f'Remove key {key}')

        return 0
    
    def stabilize(self):
        """
        Periodically stabilizes the node by verifying and updating its successors and predecessors.
        Ensures that the successor is properly linked and updates the predecessor list if needed.
        """
        while not self.shutdown_event.is_set():
            try:
                logging.info('Estabilizando nodo')

                with self.succ_lock:
                    succ = self.successors.get(0)
                succ_pred = succ.pred

                # If the predecessor of the successor is not the node itself, update it
                if (succ.id == self.id and succ_pred.id != self.id) or is_in_interval(succ_pred.id, self.id, succ.id):
                    logging.info(f'Notificando a predecesor {succ_pred}')
                    with self.succ_lock:
                        self.successors.set(0, succ_pred)
                    if succ_pred.id != self.id:
                        succ_pred.notify(self.ref)
                
                # Notify successor
                if succ.id != self.id:
                    succ.notify(self.ref)
                
                logging.info('Nodo estabilizado')

            except Exception as e:
                logging.error(f"Error en Estabilización: {e}")

            # Log the current successor and predecessor
            with self.pred_lock:
                pred = self.predecessors.get(0)
            with self.succ_lock:
                succ = self.successors.get(0)
            logging.info(f"Predecesor: {pred}, Sucesor: {succ}")

            time.sleep(10)

    def notify(self, node: NodeRef) -> int:
        """
        Notifies the node about a new predecessor.

        Args:
            node (NodeRef): The node to notify as the new predecessor.
        """
        with self.pred_lock:
            pred = self.predecessors.get(0)
            if pred.id == self.id or is_in_interval(node.id, pred.id, self.id):
                logging.info(f'Notificación del nodo {node.id}')
                with self.pred_lock:
                    if pred.id == self.id:
                        self.predecessors.erase(0)
                    self.predecessors.set(0, node)

                return TRUE
            else:
                logging.info(f'Nnguna actualización requerida para nodo {node.id}')
                return FALSE
    
    def check_predecessor(self):
        """
        Periodically checks if the predecessor node is alive.
        If the predecessor is dead, it is removed from the list of predecessors.
        """
        while True:
            try:
                with self.pred_lock:
                    pred = self.predecessors.get(0)
                if pred and pred.id != self.id:
                    logging.info(f'Revisando predecesor {pred.id}')
                    ok = pred.ping()
                    if not ok:
                        logging.info(f'Predecesor {pred.id} ha fallado')
                        with self.pred_lock:
                            preds_len = len(self.predecessors)
                            if preds_len == 1:
                                self.predecessors.erase(0)
                                self.predecessors.set(0, self.ref)
                            else:
                                self.predecessors.erase(0)
            except Exception as e:
                logging.error(f'Error en Hilo de revisión de predecesores: {e}')
            time.sleep(10)

    def check_successor(self):
        """
        Periodically checks if the successor node is alive.
        If the successor is dead, it is removed from the list of successors.
        """
        while True:
            try:
                with self.succ_lock:
                    succ = self.successors.get(0)
                if succ.id != self.id:
                    logging.info(f'Revisando sucesor {succ.id}')
                    ok = succ.ping()
                    if not ok:
                        logging.info(f'Sucesor {succ.id} ha fallado')
                        with self.succ_lock:
                            succs_len = len(self.successors)
                            if succs_len == 1:
                                self.successors.erase(0)
                                self.successors.set(0, self.ref)
                            else:
                                self.successors.erase(0)
            except Exception as e:
                logging.error(f'Error en Hilo de revisión de sucesor: {e}')
            time.sleep(10)

    def get_successor_and_notify(self, index, ip):
        """
        Retrieves the successor node and notifies it.

        Args:
            index (int): The index of the predecessor.
            ip (str): The IP address of the node.

        Returns:
            NodeRef: The successor node.
        """
        node = NodeRef(ip, self.port)

        with self.succ_lock:
            succ = self.successors.get(0)

        with self.pred_lock:
            if len(self.predecessors) <= index or self.predecessors.get(index).id != node.id:
                if len(self.predecessors) < index:
                    index = len(self.predecessors)
                self.predecessors.set(index, node)
        return succ

    def fix_successor(self, index: int) -> int:
        """
        Fixes a specific successor by retrieving the next node and updating the list.

        Args:
            index (int): The index of the successor to fix.

        Returns:
            int: The new index for the successor.
        """
        logging.info(f'Arreglando sucesor en el índice {index}')
        succ: NodeRef = None

        with self.succ_lock:
            succs_len = len(self.successors)
            if succs_len == 0:
                return 0

            if index < succs_len:
                succ = self.successors.get(index)
            last = self.successors.get(succs_len - 1)

        if succ is None:
            return 0
        
        if succ.id == self.id and succs_len == 1:
            return 0
        
        if succs_len != 1 and last.id == self.id:
            with self.succ_lock:
                succs_len -= 1
                self.successors.erase(succs_len)

        with self.succ_lock:
            try:
                succ = succ.get_successor_and_notify(index, self.ip)
                if succ.id == self.id or index == self.c - 1:
                    return 0

                if index == succs_len - 1:
                    self.successors.set(index + 1, succ)
                    return (index + 1) % len(self.successors)
                
                next_succ = self.successors.get(index + 1)
                if next_succ.id != succ.id:
                    self.successors.set(index + 1, succ)

                return (index + 1) % len(self.successors)

            except Exception as e:
                logging.error(f'Error arreglando sucesor {index}: {e}')

            return (index + 1) % len(self.successors)
    
    def fix_successors(self):
        """
        Periodically fixes the successor list by ensuring it has the correct nodes.
        Handles edge cases where the successor list is empty or incorrectly ordered.
        """
        logging.info('Hilo de Arreglo de sucesores iniciado')

        next = 0
        while not self.shutdown_event.is_set():
            try:
                succ = self.successors.get(0)
                if succ.id == self.id:
                    continue
                next = self.fix_successor(next)
            except Exception as e:
                logging.error(f'Error en Hilo de Arreglo de sucesores: {e}')
            time.sleep(15)

    def start_server(self):
        """
        Starts the main server thread to handle incoming client requests.
        
        The server listens for connections and processes different types of operations.
        Operations include key retrieval, key storage, election, and more.
        """
        logging.info('Iniciando Hilo Principal del servidor y escuchando a conecciones...')
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen(10)

            while True:
                try:
                    conn, addr = s.accept()
                    logging.info(f'Nueva conexión de {addr}')

                    data = conn.recv(1024).decode().split(SEPARATOR)

                    option = int(data[0])
                    logging.info(f'Operación {option} recibida de {addr}')
                    
                    data_response = None
                    server_response = ''

                    # Handling various operations based on option value
                    if option == FIND_ID_PREDECESSOR:
                        id = int(data[1])
                        pred = self.finger.find_predecessor(id)
                        data_response = pred if pred else self.ref
                    elif option == FIND_ID_SUCCESSOR:
                        id = int(data[1])
                        data_response = self.finger.find_successor(id)
                    elif option == GET_PREDECESSOR:
                        pred = self.predecessors.get(0)
                        data_response = pred if pred else self.ref
                    elif option == GET_SUCCESSOR:
                        succ = self.successors.get(0)
                        data_response = succ if succ else self.ref
                    elif option == CLOSEST_PRECEDING_FINGER:
                        id = int(data[1])
                        data_response = self.finger.closest_preceding_finger(id)
                    elif option == NOTIFY:
                        ip, port = data[1], int(data[2])
                        self.notify(NodeRef(ip, port))
                    elif option == GET_SUCCESSOR_AND_NOTIFY:
                        index, ip = int(data[1]), data[2]
                        data_response = self.get_successor_and_notify(index, ip)
                    elif option == PING:
                        server_response = ALIVE
                        
                    # Prepare the response to send to the client
                    if data_response:
                        response = f'{data_response.id}{SEPARATOR}{data_response.ip}'.encode()
                    else:
                        response = f'{server_response}'.encode()

                    logging.info(f'Enviando respuesta: {response}')
                    conn.sendall(response)
                    conn.close()

                except Exception as e:
                    logging.error(f'Error en Hilo Principal del servidor: {e}')