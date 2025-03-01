import threading
import logging
from typing import Dict, Tuple

class Data:
    """
    Class representing data stored in the system.
    
    :param value: Value of the data.
    :param version: Version of the data for consistency control.
    :param active: Indicates whether the data is active or marked for deletion.
    """

    def __init__(self, value: str, version: int, active: bool = True) -> None:
        self.value = value
        self.version = version
        self.active = active

    def is_empty(self) -> bool:
        """Checks if the data is empty."""
        return self.value == ''
    
    def __str__(self) -> str:
        return f'{self.value},{self.version},{self.active}'
    
    def __repr__(self) -> str:
        return f'Data(value={self.value}, version={self.version}, active={self.active})'
    
class DefaultData(Data):
    """
    Represents a default data object when a key is not present in storage.
    """

    def __init__(self) -> None:
        super().__init__('', 0)

class Storage:
    """
    Class managing data storage with support for concurrency.
    """

    def __init__(self) -> None:
        self.storage_lock = threading.RLock()  # Lock for concurrent access
        self.storage: Dict[str, Data] = {}  # Dictionary storing the data

    def get(self, key: str) -> Tuple[Data, bool]:
        """
        Retrieves a data item from storage.

        :param key: Key of the data to fetch.
        :return: A tuple containing the data and a boolean indicating if it was empty.
        """
        data = self.storage.get(key, DefaultData())
        logging.debug(f"Obteniendo llave '{key}': {data}")
        return data, data.is_empty()
    
    def set(self, key: str, data: Data) -> bool:
        """
        Stores a data item associated with a key.

        :param key: Key of the data.
        :param data: Data instance to be stored.
        :return: True if the data was stored successfully.
        """
        with self.storage_lock:
            data.active = True
            self.storage[key] = data
            logging.info(f"Llave '{key}' guardada con versión {data.version}.")
        return True
    
    def remove(self, key: str, timestamp: int, mark_inactive: bool = True) -> bool:
        """
        Removes a data item by marking it as inactive and updating its version.

        :param key: Key of the data to remove.
        :param timestamp: Timestamp of the removal.
        :param mark_inactive: Whether to mark as inactive instead of physically deleting.
        :return: True if the data was removed successfully.
        """
        with self.storage_lock:
            if key in self.storage:
                data = self.storage[key]
                if mark_inactive:
                    data.active = False
                data.version = timestamp
                self.storage[key] = data
                logging.info(f"Llave '{key}' marcada como eliminada con versión {timestamp}.")
                return True
            logging.warning(f"Se intentó eliminar una llave que no existe: '{key}'.")
        return False
    
    def get_all(self) -> Tuple[Dict[str, Data], bool]:
        """
        Retrieves all active data items from storage.

        :return: A dictionary with active data and a success boolean.
        """
        with self.storage_lock:
            active_data = {key: data for key, data in self.storage.items() if data.active}
            logging.debug(f"Se obtuvieron todos los datos activos: {len(active_data)} elementos.")
        return active_data, True
    
    def get_remove_all(self) -> Tuple[Dict[str, Data], bool]:
        """
        Retrieves all data items marked as removed.

        :return: A dictionary with removed data and a success boolean.
        """
        with self.storage_lock:
            removed_data = {key: data for key, data in self.storage.items() if not data.active}
            logging.debug(f"Se obtuvieron todos los datos eliminados: {len(removed_data)} elementos.")
        return removed_data, True
    
    def set_all(self, new_data: Dict[str, Data]) -> bool:
        """
        Stores multiple data items in the system.

        :param new_data: Dictionary of data items to store.
        :return: True if all data items were stored successfully.
        """
        with self.storage_lock:
            for key, data in new_data.items():
                data.active = True
                self.storage[key] = data
            logging.info(f"Almacenados {len(new_data)} elementos.")
        return True
    
    def remove_all(self, keys_with_versions: Dict[str, int]) -> bool:
        """
        Marks multiple keys as removed and updates their versions.

        :param keys_with_versions: Dictionary with keys and their new removal versions.
        :return: True if all data items were marked as removed successfully.
        """
        with self.storage_lock:
            for key, version in keys_with_versions.items():
                if key in self.storage:
                    data = self.storage[key]
                    data.active = False
                    data.version = version
                    self.storage[key] = data
                    logging.info(f"Llave '{key}' marcada como eliminada con versión {version}.")
                else:
                    logging.warning(f"Se intentó eliminar una llave que no existe: '{key}'.")
        return True
