import bcrypt

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt, a strong password hashing function."""
    # Generate the salt and hash the password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Return the hashed password as a decoded string for storage
    return hashed.decode('utf-8')

def verify_password(stored_hash: str, password: str) -> bool:
    """Verifies a password against a stored hash."""
    # Encode the stored hash and the input password
    stored_hash_bytes = stored_hash.encode('utf-8')
    password_bytes = password.encode('utf-8')

    # Compare the password with the stored hash
    return bcrypt.checkpw(password_bytes, stored_hash_bytes)

def store_user_passwords(user_list):
    """Stores hashed passwords for a list of users."""
    user_passwords = {}
    for username in user_list:
        password = input(f"Enter a password for user {username}: ")
        user_passwords[username] = hash_password(password)
    return user_passwords

def verify_user_login(user_passwords):
    """Verifies user login attempts."""
    username = input("Enter username: ")
    password = input("Enter password: ")

    if username in user_passwords:
        if verify_password(user_passwords[username], password):
            print("Login successful!")
        else:
            print("Incorrect password.")
    else:
        print("User not found.")

def main():
    # Create a list of users
    users = ["alice", "bob", "charlie"]

    # Store user passwords
    user_passwords = store_user_passwords(users)

    # Verify a login attempt
    verify_user_login(user_passwords)

if __name__ == "__main__":
    main()
