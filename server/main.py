from server.services.auth import start_auth
from server.services.social_graph import start_social_graph_service
from server.services.message import start_message_service
import threading

def run_services():
    # Start the authentication service
    auth_thread = threading.Thread(target=start_auth, daemon=True)
    auth_thread.start()

    # Start the social graph service
    social_graph_thread = threading.Thread(target=start_social_graph_service, daemon=True)
    social_graph_thread.start()

    # Start the message posting service
    message_thread = threading.Thread(target=start_message_service, daemon=True)
    message_thread.start()

    # Wait for all threads to finish
    auth_thread.join()
    social_graph_thread.join()
    message_thread.join()

if __name__ == "__main__":
    run_services()
