from server.services.auth import start_auth
from server.services.social_graph import start_social_graph_service
from server.services.message import start_message_service
import threading
import atexit
import time
import signal
import sys
import socket
from server.chord.node import Node
from server.repository.auth import AuthRepository
from server.repository.message import MessageRepository
from server.repository.social_graph import SocialGraphRepository
from server.config import PORT

def run_services():
    ip = socket.gethostbyname(socket.gethostname())
    node = Node(ip, PORT)

    auth_repository = AuthRepository(node) 
    message_repository = MessageRepository(node) 
    social_graph_repository = SocialGraphRepository(node) 

    # Start the authentication service
    auth_thread = threading.Thread(target=start_auth, args=("0.0.0.0:50000", auth_repository), daemon=True)
    auth_thread.start()

    # Start the message posting service
    message_thread = threading.Thread(target=start_message_service, args=("0.0.0.0:50001", message_repository, auth_repository), daemon=True)
    message_thread.start()

    # Start the social graph service
    social_graph_thread = threading.Thread(target=start_social_graph_service, args=("0.0.0.0:50002", social_graph_repository, auth_repository), daemon=True)
    social_graph_thread.start()

def graceful_exit(signal_number, frame):
    print("\nDeteniendo el programa...") 
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)

    run_services()
 
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        graceful_exit(None, None)
