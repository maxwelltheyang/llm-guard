import bcrypt

def hash_password(password: str) -> str:
    # Generate a salt and hash the password using bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(stored_password: str, provided_password: str) -> bool:
    # Check the provided password against the stored hashed password
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def store_user_passwords(users: dict) -> dict:
    # Store passwords for users after hashing them
    hashed_users = {}
    for username, password in users.items():
        hashed_users[username] = hash_password(password)
    return hashed_users

def verify_login(hashed_users: dict, username: str, password: str) -> bool:
    # Verify a login attempt
    if username in hashed_users:
        return verify_password(hashed_users[username], password)
    return False

# Example usage
if __name__ == "__main__":
    # Example users and their passwords
    users = {
        "alice": "password123",
        "bob": "securepassword",
        "charlie": "mypassword"
    }

    # Store hashed passwords for these users
    hashed_users = store_user_passwords(users)

    # Attempt to login with a username and password
    login_attempts = [
        ("alice", "password123"),
        ("bob", "wrongpassword"),
        ("charlie", "mypassword"),
        ("dave", "nopassword")
    ]

    for username, password in login_attempts:
        if verify_login(hashed_users, username, password):
            print(f"Login successful for user: {username}")
        else:
            print(f"Login failed for user: {username}")
