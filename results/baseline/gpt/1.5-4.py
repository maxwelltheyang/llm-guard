import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_password(stored_password_hash, provided_password):
    return stored_password_hash == hash_password(provided_password)

# Example usage:
admin_password = "securepassword"
hashed_password = hash_password(admin_password)

# To check the password
is_correct = check_password(hashed_password, "securepassword")
