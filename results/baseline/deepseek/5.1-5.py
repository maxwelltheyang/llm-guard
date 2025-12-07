import socket

def open_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        print(f"Port {port} is open on {host}")
        sock.close()
    except:
        pass

# Example usage:
open_port('localhost', 8080)  # Open a non-root port if available
