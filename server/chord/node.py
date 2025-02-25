import logging
import threading
import socket

from chord.utils import  getShaRepr
from chord.node_ref import NodeRef
from chord.bounded_list import BoundedList
from chord.finger_table import FingerTable
from chord.constants import *
from config import SEPARATOR

class Node:
    def __init__(self, ip: str, port: int = 8001, m: int = 160, c: int = 3):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = NodeRef(self.ip, self.port)

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

    def get_key(self, key: str) -> str:
        logging.info(f'Get key {key}')

        return ''

    def set_key(self, key: str, value: str) -> bool:
        logging.info(f'Set key {key} with value {value}')

        return 0

    def remove_key(self, key: str) -> bool:
        logging.info(f'Remove key {key}')

        return 0
    
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

                    # Prepare the response to send to the client
                    if data_response:
                        response = f'{data_response.id}{SEPARATOR}{data_response.ip}'.encode()

                    logging.info(f'Enviando respuesta: {response}')
                    conn.sendall(response)
                    conn.close()

                except Exception as e:
                    logging.error(f'Error en Hilo Principal del servidor: {e}')