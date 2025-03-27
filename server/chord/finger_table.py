import logging
import threading
import time
from chord.node_ref import NodeRef
from chord.utils import is_in_interval
from chord.constants import FIX_FINGERS_FREQ

class FingerTable:
    """
    A class representing a finger table for a Chord node.

    Attributes:
        node: The node that owns the finger table.
        m (int): The number of fingers in the table (typically 160 for a 160-bit ID space).
        finger_lock (threading.RLock): A reentrant lock to ensure thread safety while modifying the finger table.
        finger (List[NodeRef]): The list of nodes representing the finger table.
        fix_next (int): The index of the next finger to fix.
    """

    def __init__(self, node, m: int = 160) -> None:
        """
        Initializes the FingerTable with a given node and size.

        Args:
            node: The node that owns the finger table.
            m (int, optional): The number of fingers in the table. Defaults to 160.
        """
        self.node = node
        self.m = m
        self.finger_lock = threading.RLock()  # Lock for thread-safe modifications to the finger table
        self.finger = [self.node.ref] * self.m  # Initialize finger table with the node reference
        self.fix_next = 0  # Finger table index to fix next

    def find_predecessor(self, id: int) -> 'NodeRef':
        """
        Finds the predecessor of a given id.

        Args:
            id (int): The id for which to find the predecessor.

        Returns:
            NodeRef: The predecessor node for the given id.
        """
        logging.info(f'Encontrando predecesor del ID: {id}')

        node = self.node
        succ: NodeRef = node.successors.get(0)
        first = True
        while not is_in_interval(id, node.id, succ.id):
            if first:
                first = False
                node = node.finger.closest_preceding_finger(id)
            else:
                node = node.closest_preceding_finger(id)

        logging.info(f"Predecesor encontrado: {node.ref.id if first else node.id}")
        return node.ref if first else node

    def find_successor(self, id: int) -> 'NodeRef':
        """
        Finds the successor of a given id by first locating its predecessor.

        Args:
            id (int): The id for which to find the successor.

        Returns:
            NodeRef: The successor node for the given id.
        """
        logging.info(f'Encontrando sucesor del ID: {id}')

        node = self.find_predecessor(id)  # Find the predecessor of the id
        
        with self.node.succ_lock:
            if self.node.id == node.id:
                logging.info(f"El sucesor es el propio nodo, retornando el primer sucesor.")
                return self.node.successors.get(0)
            
        logging.info(f"Sucesor encontrado: {node.succ.id}")
        return node.succ  # Return successor of the node

    def closest_preceding_finger(self, id: int) -> NodeRef:
        """
        Finds the closest preceding finger to a given id.

        Args:
            id (int): The id for which to find the closest preceding finger.

        Returns:
            NodeRef: The closest preceding finger to the given id.
        """
        logging.info(f'Encontrando dedo precedente más cercano a {id}')

        for i in range(self.m - 1, -1, -1):
            with self.finger_lock:
                if self.finger[i] and is_in_interval(self.finger[i].id, self.node.id, id):
                    logging.info(f"Dedo precedente más cercano encontrado en índice {i}: {self.finger[i].id}")
                    return self.finger[i]
                
        logging.info(f"Ningún dedo precedente encontrado. Retornando la referencia del nodo {self.node.ref.id}.")
        return self.node.ref  # Return the node itself if no preceding finger is found

    def fix_fingers(self):
        """
        A method that periodically updates the finger table in a separate thread.

        The thread runs in the background and periodically attempts to update the finger table
        by finding the successor for a given id, based on the current state of the node.
        """

        logging.info('Hilo de Arreglo de dedos iniciado')

        while not self.node.shutdown_event.is_set():
            try:
                self.fix_next += 1
                if self.fix_next >= self.m:
                    self.fix_next = 0

                succ = self.find_successor((self.node.id + 2 ** self.fix_next) % 2 ** self.m)
                logging.info(f"Arreglando dedo en el índice {self.fix_next}, dedo correspondiente encontrado en {succ.id}")

                with self.finger_lock:
                    if succ.id == self.node:  # If the successor is the node itself, clear and reset the finger table
                        logging.warning(f"Sucesor del dedo {self.fix_next} es el propio nodo. Reiniciando finger table.")
                        for i in range(self.fix_next, self.m):
                            self.finger[i] = None
                        self.fix_next = 0
                        continue

                self.finger[self.fix_next] = succ  # Update the finger table with the found successor

            except Exception as e:
                logging.error(f"Error en el Hilo de Arreglo de dedos: {e}")
            time.sleep(FIX_FINGERS_FREQ)  # Sleep for a while before the next fix attempt
