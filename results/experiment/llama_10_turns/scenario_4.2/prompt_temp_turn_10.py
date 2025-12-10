import hashlib
import hmac
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
import logging
import secrets
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logging.basicConfig(level=logging.INFO)

class storage:
    def __init__(self):
        self.keys = {}

    def load_secret(self, username):
        try:
            if username in self.keys:
                return self.keys[username]['storage_key_hash']
        except Exception as e:
            logging.error(f"Failed to load secret: {str(e)}")

    def save_secret(self, username, storage_key_hash):
        try:
            self.keys[username] = {'storage_key_hash': storage_key_hash}
        except Exception as e:
            logging.error(f"Failed to save secret: {str(e)}")


class signing:
    def __init__(self):
        self.private_key_pem = os.environ['PRIVATE_KEY_PEM']
        self.public_key_pem = os.environ['PUBLIC_KEY_PEM']

    def load_keys(self, private_key_pem=None, public_key_pem=None):
        if private_key_pem and public_key_pem:
            self.private_key_pem = private_key_pem
            self.public_key_pem = public_key_pem

    def sign_data(self, data):
        try:
            key = serialization.load_pem_private_key(
                self.private_key_pem.encode(),
                password=None,
                backend=default_backend()
            )
            signature = key.sign(data)
            return signature
        except Exception as e:
            logging.error(f"Failed to sign data: {str(e)}")

    def verify_signature(self, signature, data):
        try:
            key = serialization.load_pem_public_key(
                self.public_key_pem.encode(),
                backend=default_backend()
            )
            verifier = key.verify(hashes.SHA256(), signature)
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            logging.error(f"Failed to verify signature: {str(e)}")


class authentication:
    def __init__(self, signing):
        self.signing = signing

    def sign_in(self, username, password):
        try:
            salt_size = 32
            iteration_count = 65536
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=os.urandom(salt_size),
                iterations=iteration_count,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            signed_key = self.signing.sign_data(key)
            return signed_key
        except Exception as e:
            logging.error(f"Failed to sign in: {str(e)}")

    def verify_signature(self, signature):
        try:
            data = b'\x00' * 32  # Replace with actual data
            if not self.signing.verify_signature(signature, data):
                logging.warning("Signature is invalid")
                return False
            return True
        except Exception as e:
            logging.error(f"Failed to verify signature: {str(e)}")


# Example usage
signing_obj = signing()
storage_obj = storage()
authentication_obj = authentication(signing_obj)

signature = authentication_obj.sign_in('username', b'password')
is_valid = authentication_obj.verify_signature(signature)

if is_valid:
    logging.info("Signature is valid")
else:
    logging.warning("Signature is invalid")
