from server.services.auth import start_auth
from server.services.social_graph import start_social_graph_service
from server.services.message import start_message_service
import threading
import atexit
from server.utils import save_data, load_data
import time
import signal
import sys
import socket
from server.chord.node import Node
from server.repository.auth import AuthRepository

def run_services():
    ip = socket.gethostbyname(socket.gethostname())
    node = Node(ip, 10000)

    # Load data when the server starts
    load_data()     # :skull:

    auth_repository = AuthRepository(node) 

    # Start the authentication service
    auth_thread = threading.Thread(target=start_auth, args=(auth_repository), daemon=True)
    auth_thread.start()

    # Start the social graph service
    social_graph_thread = threading.Thread(target=start_social_graph_service, daemon=True)
    social_graph_thread.start()

    # Start the message posting service
    message_thread = threading.Thread(target=start_message_service, daemon=True)
    message_thread.start()


def graceful_exit(signal_number, frame):
    print("\nDeteniendo el programa...")
    save_data()
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
