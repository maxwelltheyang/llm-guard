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

# Example usage (for demonstration purposes only)
# In practical applications, do NOT hardcode passwords; use secure methods to obtain them.
def main():
    password = input("Enter a password to hash: ")
    hashed_pw = hash_password(password)
    print("Hashed password:", hashed_pw)

    password_to_verify = input("Enter password to verify: ")
    if verify_password(hashed_pw, password_to_verify):
        print("Password correct")
    else:
        print("Password incorrect")

if __name__ == "__main__":
    main()
