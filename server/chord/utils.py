import hashlib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s -- %(levelname)s -- %(message)s')

def getShaRepr(data: str) -> int:
    """
    Compute the SHA-1 hash of a string and return its integer representation.
    
    Args:
        data (str): Input string to be hashed.
    
    Returns:
        int: Integer representation of the SHA-1 hash.
    """
    return int(hashlib.sha1(data.encode()).hexdigest(), 16)

def is_in_interval(value: int, start: int, end: int) -> bool:
    """
    Check if a given integer is within the interval (start, end].
    The interval can wrap around 0 if start > end.
    
    Args:
        value (int): Value to check.
        start (int): Start of the interval (exclusive).
        end (int): End of the interval (inclusive).
    
    Returns:
        bool: True if the value is in the interval, False otherwise.
    """
    if start < end:
        return start < value <= end
    return start < value or value <= end