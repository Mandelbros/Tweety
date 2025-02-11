from chord.utils import getShaRepr

class NodeRef:
    def __init__(self, ip: str, port: int = 10000):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port