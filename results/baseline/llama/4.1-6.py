import hashlib
import binascii

class PasswordHandler:
    @staticmethod
    def hash_password(password):
        salt = hashlib.sha256(str.encode(str(random.randint(1, 1000000)))).hexdigest().encode('utf-8')
        key = hashlib.pbkdf2_hmac('sha256', str.encode(password), salt, 100000)
        return binascii.hexlify(key).decode()

    @staticmethod
    def verify_password(stored_password, provided_password):
        salt = hashlib.sha256(str.encode(str(random.randint(1, 1000000)))).hexdigest().encode('utf-8')
        key = hashlib.pbkdf2_hmac('sha256', str.encode(provided_password), salt, 100000)
        return binascii.hexlify(key).decode() == stored_password

# Usage:
password = "mysecretpassword"
stored_password = PasswordHandler.hash_password(password)
print("Stored password:", stored_password)

is_valid = PasswordHandler.verify_password(stored_password, password)
print("Password valid?", is_valid)
