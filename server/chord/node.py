import logging
import threading
import socket
import time

from chord.utils import decode_dict, getShaRepr, is_in_interval
from chord.node_ref import NodeRef
from chord.bounded_list import BoundedList
from chord.finger_table import FingerTable
from chord.timer import Timer
from chord.storage import Data
from chord.elector import Elector
from chord.discoverer import Discoverer
from chord.replicator import Replicator
from chord.constants import *
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
        self.timer = Timer(self)
        self.elector = Elector(self, self.timer)
        self.discoverer = Discoverer(self, self.succ_lock, self.pred_lock, self.elector, self.finger)
        self.replicator = Replicator(self, self.timer)

        # Join to an existing Chord ring or create own
        self.discoverer.create_ring_or_join()
        time.sleep(6)

        threading.Thread(target=self.finger.fix_fingers, daemon=True).start()
        threading.Thread(target=self.stabilize, daemon=True).start()
        threading.Thread(target=self.check_predecessor, daemon=True).start()
        threading.Thread(target=self.check_successor, daemon=True).start()
        threading.Thread(target=self.fix_successors, daemon=True).start()
        threading.Thread(target=self.timer.update_time, daemon=True).start()
        threading.Thread(target=self.elector.check_leader, daemon=True).start()
        threading.Thread(target=self.elector.check_for_election, daemon=True).start()
        threading.Thread(target=self.discoverer.listen_for_announcements, daemon=True).start()
        threading.Thread(target=self.replicator.fix_storage, daemon=True).start()
        
        time.sleep(10)
        threading.Thread(target=self.discoverer.discover_and_join, daemon=True).start()
        
    def get_key(self, key: str) -> str:
        """
        Retrieves the value associated with a given key from the successor node.
        
        Parameters:
        - key (str): The key to retrieve.

        Returns:
        - str: The value associated with the key.
        """
        logging.info(f'Recuperar llave: {key}')
        
        key_hash = getShaRepr(key)
        with self.succ_lock:
            succ = self.finger.find_successor(key_hash)
        data = succ.retrieve_key(key)
        
        logging.info(f'Llave {key} recuperada del sucesor {succ.id}')
        return data.value

    def set_key(self, key: str, value: str) -> bool:
        """
        Sets the value for a given key on the successor node.
        
        Parameters:
        - key (str): The key to set.
        - value (str): The value to associate with the key.

        Returns:
        - bool: True if the key was successfully set, False otherwise.
        """
        logging.info(f'Fijando llave: {key} con valor: {value}')
        
        key_hash = getShaRepr(key)
        with self.succ_lock:
            succ = self.finger.find_successor(key_hash)

        with self.timer.time_lock:
            time = self.timer.time_counter

        # Store key with the timestamp and replicate if necessary
        response = succ.store_key(key, value, time, True)

        logging.info(f'Llave {key} fijada exitosamente en sucesor {succ.id}')
        return response

    def remove_key(self, key: str) -> bool:
        """
        Removes the given key from the successor node.
        
        Parameters:
        - key (str): The key to remove.

        Returns:
        - bool: True if the key was successfully removed, False otherwise.
        """
        logging.info(f'Eliminando llave: {key}')
        
        key_hash = getShaRepr(key)
        with self.succ_lock:
            succ = self.finger.find_successor(key_hash)

        with self.timer.time_lock:
            time = self.timer.time_counter

        # Delete key with the timestamp and replicate if necessary
        response = succ.delete_key(key, time, True)

        logging.info(f'Llave {key} eliminada exitosamente del sucesor {succ.id}')
        return response
    
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
                        self.replicator.replicate_all_data(succ_pred)
                
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

                self.replicator.handle_new_predecessor()
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
                    self.replicator.replicate_all_data(succ)
                    return (index + 1) % len(self.successors)
                
                next_succ = self.successors.get(index + 1)
                if next_succ.id != succ.id:
                    self.successors.set(index + 1, succ)

                    find = False
                    for i in range(len(self.successors)):
                        if succ.id == self.successors.get(i).id:
                            find = True

                    if find:
                        self.replicator.replicate_all_data(succ)

                return (index + 1) % len(self.successors)

            except Exception as e:
                logging.error(f'Error arreglando sucesor {index}: {e}')
                with self.succ_lock:
                    self.successors.erase(index)
                    if len(self.successors) == 0:
                        self.successors.set(0, self.ref)
                    return index % len(self.successors)
    
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
                    elif option == PING_LEADER:
                        id, time = int(data[1]), int(data[2])
                        server_response = self.elector.ping_leader(id, time)
                    elif option == ELECTION:
                        id, ip, port = int(data[1]), data[2], int(data[3])
                        server_response = self.elector.election(id, ip, port)
                    elif option == SET_PARTITION:
                        dict = decode_dict(data[1])
                        version = decode_dict(data[2])
                        removed_dict = decode_dict(data[3])
                        server_response = self.replicator.set_partition(dict, version, removed_dict)
                    elif option == RESOLVE_DATA:
                        dict = decode_dict(data[1])
                        version = decode_dict(data[2])
                        removed_dict = decode_dict(data[3])
                        server_response = self.replicator.resolve_data(dict, version, removed_dict)
                    elif option == RETRIEVE_KEY:
                        key = data[1]
                        server_response = self.replicator.get(key)
                    elif option == STORE_KEY:
                        key = data[1]
                        value, version = data[2], int(data[3])
                        rep = True if int(data[4]) == TRUE else False
                        server_response = self.replicator.set(key, Data(value, version), rep)
                    elif option == DELETE_KEY:
                        key, time = data[1], data[2]
                        rep = True if int(data[3]) == TRUE else False
                        server_response = self.replicator.remove(key, time, rep)
                        
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