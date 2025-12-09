import bcrypt

def hash_password(password: str) -> str:
    """Hash a password for storage using bcrypt."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a hashed password against one provided by user."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def store_user_passwords(user_passwords: dict) -> dict:
    """Store hashed passwords for a list of users."""
    hashed_passwords = {}
    for user, password in user_passwords.items():
        hashed_passwords[user] = hash_password(password)
    return hashed_passwords

def verify_login(users: dict, username: str, password_attempt: str) -> bool:
    """Verify a user's login attempt with stored password hashes."""
    if username in users:
        return verify_password(users[username], password_attempt)
    return False

# Example usage
user_credentials = {
    'user1': 'password123',
    'user2': 'mysecurepassword',
    'user3': 'anotherpassword'
}

# Store hashed passwords for the users
stored_passwords = store_user_passwords(user_credentials)

# Verify login attempts
print(verify_login(stored_passwords, 'user1', 'password123'))  # True
print(verify_login(stored_passwords, 'user2', 'wrongpassword')) # False
print(verify_login(stored_passwords, 'user3', 'anotherpassword')) # True
