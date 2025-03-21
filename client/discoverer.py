import streamlit as st
import socket, logging
import grpc
import struct
from config import MULTICAST_GROUP, MULTICAST_PORT, TIMEOUT, ARE_YOU, YES_IM, SEPARATOR

MESSAGE = f"{ARE_YOU}{SEPARATOR}0".encode()

logging.basicConfig(level=logging.INFO)  # Set the log level to INFO

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
    
    if "server" not in st.session_state:
        st.session_state["server"] = None

    server = st.session_state["server"]

    if not server or not is_alive(server, int(service)):
        update_server()
        server = st.session_state["server"]

    if server and is_alive(server, int(service)):
        return f"{server}:{service}"

    raise ConnectionError("No available servers are alive.")

def update_server():
    """
    Update the server information in the session state.

    This function discovers a new server and updates the session state with the new server information.
    If no server is found, it logs an info message and removes the server from the session state if it exists.
    """
    server = discover()
    if server:
        logging.info(f"Discoverer found {server}")
        st.session_state['server'] = server[0]
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
    if not host:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False
    
def discover():
    # Crear socket UDP y ligar al puerto multicast para recibir respuestas
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('', MULTICAST_PORT))
    except Exception as e:
        logging.error(f"Error al hacer bind del socket: {e}")
        raise

    sock.settimeout(TIMEOUT)

    # Configurar TTL para el paquete multicast
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    # Deshabilitar el loopback multicast para no recibir nuestro propio mensaje
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

    try:
        # Unirse al grupo multicast para recibir respuestas
        group = socket.inet_aton(MULTICAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Enviar el mensaje de descubrimiento
        sock.sendto(MESSAGE, (MULTICAST_GROUP, MULTICAST_PORT))
        logging.info(f"Multicast enviado a {(MULTICAST_GROUP, MULTICAST_PORT)}: {MESSAGE.decode()}")

        # Esperar respuestas válidas
        while True:
            try:
                data, server = sock.recvfrom(1024)
                decoded = data.decode().strip()
                logging.info(f"Respuesta recibida de {server}: {decoded}")

                # Si se recibe el mismo mensaje de descubrimiento, se ignora
                if data == MESSAGE:
                    logging.info("Recibido eco del mensaje de descubrimiento, ignorando.")
                    continue

                # Parsear la respuesta usando el separador
                parts = decoded.split(SEPARATOR)
                if len(parts) != 2:
                    logging.info(f"Mensaje mal formado, ignorando: {decoded}")
                    continue

                prefix, leader_info = parts
                if prefix != YES_IM:
                    logging.info(f"Mensaje no válido (prefijo incorrecto): {decoded}")
                    continue

                # Si la respuesta es válida, retornar la IP del servidor y la info del líder
                logging.info(f"Respuesta válida recibida: {decoded} desde {server[0]}")
                return server[0], leader_info

            except socket.timeout:
                logging.info("Timeout esperando respuesta de servidor.")
                break
    except Exception as e:
        logging.error(f"Error durante la búsqueda de servidores: {e}")
    finally:
        sock.close()

    raise RuntimeError("No se encontró ningún servidor disponible.")


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