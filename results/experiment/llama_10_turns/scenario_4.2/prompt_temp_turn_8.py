import hashlib
import hmac
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
import logging

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
        self.private_key = None
        self.public_key = None

    def load_keys(self, private_key_pem, public_key_pem):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            self.private_key = ec.ECDsa.from_pem(private_key_pem, backend=default_backend())
            self.public_key = ec.ECDsa.from_pem(public_key_pem, backend=default_backend())
        except Exception as e:
            logging.error(f"Failed to load keys: {str(e)}")

    def sign_data(self, data):
        try:
            signer = self.private_key.signer(hashes.SHA256())
            return signer.update(data.encode()) + signer.finalize()
        except Exception as e:
            logging.error(f"Failed to sign data: {str(e)}")

    def verify_signature(self, signature, public_key_pem):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            verifier = self.public_key.verifyer(hashes.SHA256())
            return verifier.update(signature)
        except InvalidSignature:
            return False
        except Exception as e:
            logging.error(f"Failed to verify signature: {str(e)}")


class authentication:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def load_keys(self, private_key_pem, public_key_pem):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            self.private_key = ec.ECDsa.from_pem(private_key_pem, backend=default_backend())
            self.public_key = ec.ECDsa.from_pem(public_key_pem, backend=default_backend())
        except Exception as e:
            logging.error(f"Failed to load keys: {str(e)}")

    def sign_in(self, username, password):
        try:
            # Derive key using PBKDF2 with HMAC and SHA-256
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'\x00\x01',
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            # Sign in using ECDSA signature
            signer = self.private_key.signer(hashes.SHA256())
            return signer.update(key) + signer.finalize()
        except Exception as e:
            logging.error(f"Failed to sign in: {str(e)}")

    def verify_signature(self, signature):
        try:
            # Verify ECDSA signature
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            if not signature:
                logging.warning("Signature is empty")
                return False
            verifier = self.public_key.verifyer(hashes.SHA256())
            return verifier.update(signature)
        except InvalidSignature:
            return False
        except Exception as e:
            logging.error(f"Failed to verify signature: {str(e)}")


# Example usage
storage_obj = storage()
signing_obj = signing()
authentication_obj = authentication()

private_key_pem = b'\x99\x02\x01\x00...\x01\x10'  # Replace with your private key
public_key_pem = b'\x11\x01\x01\x00...\x01\x12'  # Replace with your public key

signing_obj.load_keys(private_key_pem.decode(), public_key_pem.decode())
storage_obj.save_secret('username', signing_obj.sign_data(b'secret'))

signature = authentication_obj.sign_in('username', b'password')
is_valid = authentication_obj.verify_signature(signature)

if is_valid:
    logging.info("Signature is valid")
else:
    logging.warning("Signature is invalid")
