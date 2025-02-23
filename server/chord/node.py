import logging
from chord.utils import  getShaRepr
from chord.node_ref import NodeRef

class Node:
    def __init__(self, ip: str, port: int = 8001):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = NodeRef(self.ip, self.port)

    def get_key(self, key: str) -> str:
        logging.info(f'Get key {key}')

        return ''

    def set_key(self, key: str, value: str) -> bool:
        logging.info(f'Set key {key} with value {value}')

        return 0

    def remove_key(self, key: str) -> bool:
        logging.info(f'Remove key {key}')

        return 0