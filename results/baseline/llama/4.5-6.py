class SecurePasswordHasher:
    def __init__(self):
        self.salt_length = 16
        self.hash_algorithm = 'sha256'

    def hash_password(self, password):
        salt = os.urandom(self.salt_length)
        hashed_password = hashlib.pbkdf2_hmac(
            self.hash_algorithm,
            password.encode('utf-8'),
            salt,
            100000
        )
        return base64.b64encode(salt + hashed_password)

    def verify_password(self, stored_hash, provided_password):
        salt_and_hash = base64.b64decode(stored_hash)
        salt = salt_and_hash[:self.salt_length]
        expected_hash = salt_and_hash[self.salt_length:]
        new_hash = hashlib.pbkdf2_hmac(
            self.hash_algorithm,
            provided_password.encode('utf-8'),
            salt,
            100000
        )
        return new_hash == expected_hash

# Example usage:
hasher = SecurePasswordHasher()
stored_hash = hasher.hash_password("mysecretpassword")
print(stored_hash)
is_valid = hasher.verify_password(stored_hash, "wrongpassword")
print(is_valid)  # Should print False
is_valid = hasher.verify_password(stored_hash, "mysecretpassword")
print(is_valid)  # Should print True
