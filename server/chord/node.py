import logging
import threading

from chord.utils import  getShaRepr
from chord.node_ref import NodeRef
from chord.bounded_list import BoundedList
from chord.finger_table import FingerTable

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