from typing import Generic, List, TypeVar
import logging

T = TypeVar('T')

class BoundedList(Generic[T]):
    """
    A class to represent a bounded list with a fixed capacity.

    Attributes:
        capacity (int): The maximum capacity of the list.
        default (T): The default value returned when an index is out of range.
        list (List[T]): The internal list holding the items.
    """
    def __init__(self, capacity: int, default: T):
        """
        Initializes the bounded list with a given capacity and default value.

        Args:
            capacity (int): The maximum number of elements the list can hold.
            default (T): The default value to return when accessing an invalid index.
        """
        self.capacity = capacity
        self.default = default
        self.list: List[T] = []

    def get(self, index: int) -> T:
        """
        Gets the item at the specified index, returning the default value if out of range.

        Args:
            index (int): The index of the item to retrieve.

        Returns:
            T: The item at the given index or the default value if the index is out of range.
        """
        try:
            return self.list[index]
        except IndexError:
            # Log error with more details about the invalid access attempt
            logging.warning(f"Índice {index} fuera de rango. Retornando valor por defecto: {self.default}")
            return self.default

    def set(self, index: int, value: T):
        """
        Sets a value at the specified index, inserting the value at the correct position,
        and trimming the list if it exceeds the capacity.

        Args:
            index (int): The index where the value should be inserted.
            value (T): The value to set at the specified index.
        """
        new_list = self.list[:index] + [value] + self.list[index:]

        # Ensure the list does not exceed the specified capacity
        if len(new_list) > self.capacity:
            new_list = new_list[:self.capacity]
            # Log the truncation event
            logging.info(f"Capacidad de la lista excedida. Truncando la lista a {self.capacity} elementos.")

        self.list = new_list

    def erase(self, index: int):
        """
        Removes the item at the specified index from the list.

        Args:
            index (int): The index of the item to remove.
        """
        self.list = self.list[:index] + self.list[index + 1:]
        # Log the removal event with the index
        logging.info(f"El elemento en el índice {index} ha sido eliminado.")

    def clear(self):
        """
        Clears all items from the list.
        """
        self.list = []
        # Log the clearing of the list
        logging.info("La lista ha sido vaciada.")

    def __len__(self) -> int:
        """
        Returns the number of items currently in the list.

        Returns:
            int: The current size of the list.
        """
        return len(self.list)
