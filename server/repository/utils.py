import base64 
import logging
import grpc
from chord.node import Node

logging.basicConfig(level=logging.INFO)

def exists(node: Node, path):
    logging.info(f"Checking if file exists: {path}")

    exists = node.get_key(path) != ''
    if not exists:
        logging.info("File doesn't exist")
        return False, None
    
    logging.info(f"File already exists: {path}")
    return True, None

def save(node: Node, obj, path):
    logging.info(f"Saving file: {path}")

    try:
        data = obj.SerializeToString()
    except Exception as e:
        logging.error(f"Error serializing object: {e}")
        return grpc.StatusCode.INTERNAL

    str_data = base64.b64encode(data).decode('utf-8')

    ok = node.set_key(path, str_data)
    if not ok:
        logging.error("Error saving file")
        return grpc.StatusCode.INTERNAL
    return None

def load(node: Node, path, obj):
    logging.info(f"Loading file: {path}")

    data_str = node.get_key(path)
    if data_str == '':
        logging.error(f"Error getting file")
        return None, grpc.StatusCode.NOT_FOUND

    try:
        data = base64.b64decode(data_str)
        obj.ParseFromString(data)
    except Exception as e:
        logging.error(f"Error decoding object: {e}")
        return None, grpc.StatusCode.INTERNAL

    return obj, None

def delete(node: Node, path):
    logging.info(f"Deleting file: {path}")

    ok = node.remove_key(path)
    if not ok:
        logging.error(f"Error deleting file")
        return grpc.StatusCode.INTERNAL

    return None