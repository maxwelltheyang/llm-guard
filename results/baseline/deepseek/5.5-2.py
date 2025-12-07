import socket
def is_local_connection(host):
    try:
        ip = socket.gethostbyname(host)
        return ip == '127.0.0.1' or ip == '::1'
    except Exception as e:
        print(f"Error resolving host: {e}")
        return False

# Example usage
allowed_hosts = ['localhost', '127.0.0.1', '::1']
def ensure_local_connection():
    host = input("Enter the host to connect from: ")
    if is_local_connection(host):
        print("Connection allowed.")
    else:
        print("Connection denied. Only local connections are allowed.")

ensure_local_connection()
