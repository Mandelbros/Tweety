import logging
import time
from typing import Dict
from chord.storage import Data, DefaultData, Storage
from chord.node_ref import NodeRef
from chord.constants import FALSE, TRUE
from chord.bounded_list import BoundedList
from chord.utils import encode_dict, decode_dict, getShaRepr, is_in_interval
from chord.timer import Timer
from config import SEPARATOR


class Replicator:
    """
    A class responsible for handling the replication of data in the Chord distributed system.
    It manages the processes of storing, replicating, and resolving data across multiple nodes.
    """

    def __init__(self, node, timer: Timer) -> None:
        """
        Initializes the replicator with the associated node and timer for synchronization.

        Args:
            node: The node associated with this replicator instance.
            timer: The timer used for synchronization tasks.
        """
        self.node = node
        self.timer = timer
        self.storage = Storage()  # Storage instance for key-value pairs

    def get(self, key: str) -> str:
        """
        Retrieves the value and version of the data associated with the given key.

        Args:
            key: The key to retrieve data for.

        Returns:
            A string containing the value and version of the data associated with the key.
        """
        with self.storage.storage_lock:
            data, error = self.storage.get(key)
            if error:
                data = DefaultData()  # Default to an empty data object if an error occurs
            
            # Return the value and version, separated by a constant separator
            return f'{data.value}{SEPARATOR}{data.version}'
        
    def set(self, key: str, data: Data, rep: bool) -> str:
        """
        Stores the data for the given key and attempts to replicate it if necessary.

        Args:
            key: The key to store data for.
            data: The data to be stored.
            rep: A flag indicating whether to replicate the data.

        Returns:
            A string indicating the success or failure of the operation.
        """
        logging.info(f'Guardando llave {key}')

        # Store the data in local storage
        with self.storage.storage_lock:
            self.storage.set(key, data)

        with self.node.succ_lock:
            succ: NodeRef = self.node.successors.get(0)

        # Replicate data if the flag is set and the successor is different from the current node
        if rep and succ.id != self.node.id:
            try:
                self.replicate_set(key, data)
            except Exception as e:
                logging.error(f'Error replicando dato con llave {key} y valor {data.value} desde {succ.ip}: {e}')
                return FALSE

        return TRUE
        
    def replicate_set(self, key: str, data: Data):
        """
        Replicates the data to all successors of the current node.

        Args:
            key: The key associated with the data.
            data: The data to be replicated.
        """
        logging.info(f'Replicando llave {key}')

        with self.node.succ_lock:
            successors: BoundedList[NodeRef] = self.node.successors

            # Attempt to replicate the data to each successor
            for i in range(len(successors)):
                try:
                    succ_i = successors.get(i)
                    logging.info(f'Configurando réplica para la llave {key} en {succ_i.ip}')
                    ok = succ_i.store_key(key, data.value, data.version)
                    if not ok:
                        logging.error(f'Error replicando llave {key} en sucesor {i}')
                except Exception as e:
                    logging.error(f'Error replicando llave {key} en sucesor {i}: {e}')

    def remove(self, key: str, time: int, rep: bool) -> bool:
        """
        Removes the key from the local storage and attempts to replicate the removal to successors.

        Args:
            key: The key to remove.
            time: The timestamp associated with the removal.
            rep: A flag indicating whether to replicate the removal.

        Returns:
            A boolean indicating whether the removal was successful.
        """
        with self.storage.storage_lock:
            self.storage.remove(key, time)

        with self.node.succ_lock:
            succ: NodeRef = self.node.successors.get(0)

        # Replicate removal if the flag is set and the successor is different from the current node
        if rep and succ.id != self.node.id:
            try:
                self.replicate_remove(key, time)
            except Exception as e:
                logging.error(f'Error eliminando llave {key} desde {succ.ip}: {e}')
                return FALSE

        return TRUE
    
    def replicate_remove(self, key: str, time: int):
        """
        Replicates the removal of a key to all successors.

        Args:
            key: The key to be removed.
            time: The timestamp associated with the removal.
        """
        logging.info(f'Eliminando llave {key}')

        with self.node.succ_lock:
            successors: BoundedList[NodeRef] = self.node.successors

            # Attempt to remove the key from each successor
            for i in range(len(successors)):
                try:
                    succ_i = successors.get(i)
                    logging.info(f'Eliminando la réplica de la llave {key} de {succ_i.ip}')
                    ok = succ_i.delete_key(key, time)
                    if not ok:
                        logging.error(f'Error eliminando llave {key} en sucesor {i}')
                except Exception as e:
                    logging.error(f'Error eliminando llave {key} en sucesor {i}: {e}')

    def set_partition(self, dict: Dict[str, str], version: Dict[str, int], removed_dict: Dict[str, int]) -> bool:
        """
        Updates the storage with a partition of data, including new values and removed keys.

        Args:
            dict: A dictionary of new data to be stored.
            version: A dictionary of versions corresponding to the new data.
            removed_dict: A dictionary of keys that have been removed.

        Returns:
            A boolean indicating whether the partition update was successful.
        """
        new_dict: Dict[str, Data] = {}

        # Convert the new data to Data objects
        for key in dict.keys():
            new_dict[key] = Data(dict[key], version[key])

        # Attempt to update the storage with the new and removed data
        with self.storage.storage_lock:
            try:
                self.storage.set_all(new_dict)
                self.storage.remove_all(removed_dict)
            except Exception as e:
                logging.error(f'Error configurando partición: {e}')
                return FALSE
            
        return TRUE

    def replicate_all_data(self, node: NodeRef):
        """
        Replicates all data to a given node, including both stored and removed data.

        Args:
            node: The node to which the data will be replicated.
        """
        with self.node.pred_lock:
            pred = self.node.predecessors.get(0)

        if pred.id == self.node.id:
            return
        
        logging.info(f'Replicando todos los datos a {node.ip}')

        # Retrieve all the data to be replicated
        with self.storage.storage_lock:
            dict, _ = self.storage.get_all()
            removed_dict, _ = self.storage.get_remove_all()

        new_dict: Dict[str, str] = {}
        new_version: Dict[str, int] = {}
        new_removed_dict: Dict[str, int] = {}

        # Filter the data to be replicated based on valid range
        for key, data in dict.items():
            if is_in_interval(getShaRepr(key), pred.id, self.node.id):
                new_dict[key] = data.value
                new_version[key] = data.version

        for key, data in removed_dict.items():
            if is_in_interval(getShaRepr(key), pred.id, self.node.id):
                new_removed_dict[key] = data.version

        # Attempt to replicate the data to the given node
        ok = node.set_partition(encode_dict(new_dict), encode_dict(new_version), encode_dict(new_removed_dict))
        if not ok:
            logging.error(f'Error replicando todos los datos a {node.ip}')

    def resolve_data(self, dict: Dict[str, str], version: Dict[str, int], removed_dict: Dict[str, int]) -> str:
        """
        Resolves conflicts between different versions of the same data by comparing versions and updating accordingly.

        Args:
            dict: A dictionary of new data to resolve.
            version: A dictionary of versions corresponding to the new data.
            removed_dict: A dictionary of removed keys.

        Returns:
            A string containing the resolved data.
        """
        logging.info('Resolviendo conflictos de versiones de datos')

        new_dict: Dict[str, Data] = {}
        res_dict_value: Dict[str, str] = {}
        res_dict_version: Dict[str, int] = {}
        res_removed_dict: Dict[str, int] = {}

        with self.storage.storage_lock:
            actual_dict, error = self.storage.get_all()
            if not error:
                return ''

            # Resolve conflicts for each data item
            for key, value in dict.items():
                try:
                    data = actual_dict[key]
                except:
                    data = DefaultData()

                if data.version > version[key]:
                    res_dict_value[key] = data.value
                    res_dict_version[key] = data.version
                else:
                    new_dict[key] = Data(value, version[key])

            # Resolve removals
            for key, time in removed_dict.items():
                try:
                    data = actual_dict[key]
                except:
                    data = DefaultData()

                if data.version > time:
                    res_dict_value[key] = data.value
                    res_dict_version[key] = data.version
                else:
                    self.storage.remove(key, time)

            # Resolve removals across all data
            remove, _ = self.storage.get_remove_all()

            for key, data in remove.items():
                time = version[key]

                if data.version > time:
                    res_removed_dict[key] = data.version

            # Update the storage with resolved data
            self.storage.set_all(new_dict)

            # Return the encoded resolved data
            return f'{encode_dict(res_dict_value)}{SEPARATOR}{encode_dict(res_dict_version)}{SEPARATOR}{encode_dict(res_removed_dict)}'

    def handle_new_predecessor(self):
        """
        Handles the process of assigning data to a new predecessor after a node joins the ring.
        """
        with self.node.succ_lock:
            pred: NodeRef = self.node.predecessors.get(0)
            pred_pred: NodeRef
            if len(self.node.predecessors) > 1:
                pred_pred = self.node.predecessors.get(1)
            else:
                pred_pred = self.node.ref

        if pred.id == pred_pred.id:
            return
        
        logging.info('Delegando datos del predecesor')

        # Retrieve current storage data
        with self.storage.storage_lock:
            dict, _ = self.storage.get_all()
            remove, _ = self.storage.get_remove_all()

        new_dict: Dict[str, str] = {}
        new_version: Dict[str, int] = {}
        new_removed_dict: Dict[str, int] = {}

        # Filter data to be delegated to the new predecessor
        for key, data in dict.items():
            if not is_in_interval(getShaRepr(key), pred_pred.id, pred.id):
                continue

            new_dict[key] = data.value
            new_version[key] = data.version

        for key, data in remove.items():
            if not is_in_interval(getShaRepr(key), pred_pred.id, pred.id):
                continue

            new_removed_dict[key] = data.version

        # Resolve and set the data in the new predecessor
        response, ok = pred.resolve_data(encode_dict(new_dict), encode_dict(new_version), encode_dict(new_removed_dict))
        if not ok:
            logging.error(f'Error obteniendo datos de {pred.ip}')
            return
        
        # Decode and store the resolved data
        res_dict: Dict[str, str] = decode_dict(response[0])
        res_version: Dict[str, int] = decode_dict(response[1])
        res_removed_dict: Dict[str, int] = decode_dict(response[2])

        new_res_dict: Dict[str, Data] = {}

        for key, value in res_dict.items():
            new_res_dict[key] = Data(value, res_version[key])
        
        with self.storage.storage_lock:
            self.storage.set_all(new_res_dict)
            self.storage.remove_all(res_removed_dict)

    def fix_storage(self):
        while True:
            try:
                logging.info('Arreglando almacenamiento')

                with self.storage.storage_lock:
                    dict, _ = self.storage.get_all()
                    logging.info(f'Longitud actual de almacenamiento: {len(dict)}')

                with self.node.succ_lock:
                    succ_len = len(self.node.successors)

                with self.node.pred_lock:
                    while len(self.node.predecessors) > succ_len:
                        self.node.predecessors.erase(len(self.node.predecessors) - 1)
                        if len(self.node.predecessors) == 0:
                            self.node.predecessors.set(0, self.node.ref)
                            break

                with self.node.pred_lock:
                    pred: NodeRef = self.node.predecessors.get(len(self.node.predecessors) - 1)

                if pred.id != self.node.id:
                    pred_pred = pred.pred

                    if pred_pred.id != self.node.id and pred_pred.id != pred.id:
                        with self.timer.time_lock:
                            time_c = self.timer.time_counter
                        for key in dict.keys():
                            if is_in_interval(getShaRepr(key), pred_pred.id, self.node.id):
                                continue

                            self.storage.remove(key, time_c, False)
            except Exception as e:
                logging.error(f'Error en hilo de arreglo de almacenamiento: {e}')

            time.sleep(10)