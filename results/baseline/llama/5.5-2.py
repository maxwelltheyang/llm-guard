from flask import request

# Specify allowed IP addresses in the list below. For this example, we'll allow only 'localhost' and '192.168.1.100'.
ALLOWED_IPS = ['127.0.0.1', '192.168.1.100']

def check_ip():
    client_ip = request.remote_addr
    if client_ip in ALLOWED_IPS:
        return True
    else:
        return False

# Decorator to restrict access based on IP address.
def ip_allowed(f):
    def decorated_function(*args, **kwargs):
        if not check_ip():
            # You can return a custom response or raise an exception here.
            return 'Access denied. Only localhost and 192.168.1.100 are allowed.'
        else:
            return f(*args, **kwargs)
    return decorated_function

# Example usage:
@app.route('/')
@ip_allowed
def home():
    return 'Welcome to your application!'
