import streamlit as st
import socket, logging
from cache import FileCache
import grpc

def get_host(service):
    """
    Get the host address for a given service.

    This function checks if the server stored in the session state is alive for the given service.
    If not, it updates the server information and checks again. If a live server is found, it returns
    the server address with the service port.

    Args:
        service (int): The service port number.

    Returns:
        str: The server address with the service port.

    Raises:
        ConnectionError: If no available servers are alive.
    """
    
    server = st.session_state['server']

    if not is_alive(server, int(service)):
        update_server()
        server = st.session_state['server']

    if server and is_alive(server, int(service)):
        return (f"{server}:{service}")

    raise ConnectionError("No available servers are alive.")

def update_server():
    """
    Update the server information in the session state.

    This function discovers a new server and updates the session state with the new server information.
    If no server is found, it logs an info message and removes the server from the session state if it exists.
    """
    server = discover()
    if server:
        st.session_state['server'] = server
    else:
        logging.info("No servers found")

        if st.session_state.get('server'):
            del st.session_state['server']

def is_alive(host, port, timeout=2):
    """
    Check if a server is alive.

    This function attempts to create a connection to the given host and port within the specified timeout.
    If the connection is successful, it returns True. Otherwise, it returns False.

    Args:
        host (str): The server host address.
        port (int): The server port number.
        timeout (int, optional): The connection timeout in seconds. Defaults to 2.

    Returns:
        bool: True if the server is alive, False otherwise.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    
def discover():
    pass


def get_authenticated_channel(host, token):
    """
    Get an authenticated gRPC channel.

    This function creates an authenticated gRPC channel using the provided host and token.

    Args:
        host (str): The server host address.
        token (str): The authentication token.

    Returns:
        grpc.Channel: The authenticated gRPC channel.
    """
    auth_interceptor = AuthInterceptor(token)
    return grpc.intercept_channel(grpc.insecure_channel(host), auth_interceptor)


class AuthInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamClientInterceptor):
    """
    Interceptor for adding authentication token to gRPC calls.

    This class intercepts gRPC calls and adds the provided authentication token to the metadata.

    Args:
        token (str): The authentication token.
    """
    def __init__(self, token):
        self.token = token

    def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = client_call_details.metadata if client_call_details.metadata is not None else []
        metadata = list(metadata) + [('authorization', self.token)]
        client_call_details = client_call_details._replace(metadata=metadata)
        return continuation(client_call_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        metadata = client_call_details.metadata if client_call_details.metadata is not None else []
        metadata = list(metadata) + [('authorization', self.token)]
        client_call_details = client_call_details._replace(metadata=metadata)
        return continuation(client_call_details, request)