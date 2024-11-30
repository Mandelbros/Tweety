from server.services.auth import start_auth
from server.services.social_graph import start_social_graph_service
import threading

if __name__ == "__main__":
    # Run both services in separate threads
    auth_thread = threading.Thread(target=start_auth)
    social_graph_thread = threading.Thread(target=start_social_graph_service)

    auth_thread.start()
    social_graph_thread.start()

    auth_thread.join()
    social_graph_thread.join()