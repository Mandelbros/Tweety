import hashlib
import logging
import json
import struct
import socket

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

def encode_dict(data: dict) -> str:
    """
    Convert a dictionary into a JSON-formatted string, stripping whitespace from keys.
    
    Args:
        data (dict): Dictionary to encode.
    
    Returns:
        str: JSON string representation of the dictionary, or an empty string on failure.
    """
    try:
        clean_dict = {k.strip(): v for k, v in data.items()}
        return json.dumps(clean_dict)
    except (TypeError, ValueError) as e:
        logging.error(f"Fallo al codificar diccionario: {e}")
        return ''

def decode_dict(json_str: str) -> dict:
    """
    Parse a JSON-formatted string into a dictionary.
    
    Args:
        json_str (str): JSON string to decode.
    
    Returns:
        dict: Decoded dictionary, or an empty dictionary on failure.
    """
    try:
        return json.loads(json_str)
    except (TypeError, ValueError) as e:
        logging.error(f"Fallo al decodificar cadena JSON: {e}")
        return {}
    
def send_message(sock: socket.socket, message: bytes):
    """
    Sends a message prefixing its length to 4 bytes.
    """
    msg_length = struct.pack('!I', len(message))
    sock.sendall(msg_length + message)

def recvall(sock: socket.socket, n: int) -> bytes:
    """
    Reads exactly n bytes from the socket.
    """
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            break  # If nothing more is received, the accumulated data is returned
        data += packet
    return data

def recv_message(sock: socket.socket) -> bytes:
    """
    Receives a complete message. First, reads the header (4 bytes), 
    which indicates the size, and then reads that number of bytes.
    """
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return b''
    msglen = struct.unpack('!I', raw_msglen)[0]
    return recvall(sock, msglen)