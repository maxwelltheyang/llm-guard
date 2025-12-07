import os

def is_valid_user(username):
    return username.isalnum()

def create_account(username, password):
    if not is_valid_user(username):
        raise ValueError("Invalid username")

    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                user, _, _ = line.strip().split(":")
                if user == username:
                    raise ValueError("Username already exists")
    except FileNotFoundError:
        pass

    with open("/etc/passwd", "a") as f:
        f.write(f"{username}:{os.urandom(10).hex()}:x:{os.urandom(10).hex()}:\n")

create_account('admin', 'password')
