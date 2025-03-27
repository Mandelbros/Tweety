import logging
import threading
import time
from typing import Dict
from collections import defaultdict

class Timer:
    """
    Timer class that manages the time for a node in the Chord network and 
    synchronizes the time using the Berkeley algorithm.
    """

    def __init__(self, node):
        """
        Initializes the node's timer.

        :param node: Instance of the node associated with this timer.
        """
        self.node = node
        now = int(time.time())

        # Local time counter for the node
        self.time_counter = now

        # Dictionary that stores the times reported by each node
        self.node_timers: Dict[int, int] = defaultdict(int)
        self.node_timers[self.node.id] = now

        # Lock for time synchronization
        self.time_lock = threading.Lock()

    def berkeley_algorithm(self) -> int:
        """
        Implements the Berkeley algorithm for time synchronization in distributed nodes.

        :return: The average time calculated based on the clocks of the known nodes.
        """
        if not self.node_timers:
            logging.warning("Algoritmo de Berkeley ejecutado con un diccionario node_timers vacío.")
            return self.time_counter  # Returns the local time if there are no external references

        total_time = sum(self.node_timers.values())
        average_time = total_time // len(self.node_timers)

        logging.info(f"Algoritmo de Berkeley computó tiempo promedio: {average_time}")
        return average_time

    def update_time(self):
        """
        Thread that periodically increments the node's local time and updates it in the time dictionary.
        """
        logging.info(f"Iniciando Hilo de actualización de tiempo del nodo {self.node.id}")
        
        while not self.node.shutdown_event.is_set():
            try:
                with self.time_lock:
                    self.time_counter += 1
                    self.node_timers[self.node.id] += 1
                logging.debug(f"Nodo {self.node.id} con tiempo actualizado: {self.time_counter}")
            except Exception as e:
                logging.error(f"Error en Hilo de actualización de tiempo del nodo {self.node.id}: {e}")

            time.sleep(1)  # Increment the time in one-second intervals
