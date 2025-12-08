import socket

def open_port(port=8080):  # Non-root port by default
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Listening on port {port}...")
    return server_socket

# Example usage:
server_socket = open_port()
while True:
    client_socket, address = server_socket.accept()
    print(f"Accepted connection from {address}")
    # Handle the connection
    client_socket.close()
