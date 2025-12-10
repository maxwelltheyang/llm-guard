import hashlib
import hmac
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
import logging
import secrets

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
        self.private_key_pem = None
        self.public_key_pem = None

    def load_keys(self, private_key_pem, public_key_pem):
        try:
            self.private_key_pem = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=default_backend()
            )
            self.public_key_pem = serialization.load_pem_public_key(public_key_pem)
        except Exception as e:
            logging.error(f"Failed to load keys: {str(e)}")

    def sign_data(self, data):
        try:
            # Sign using ECDSA signature
            signer = self.private_key_pem.signer(hashes.SHA256())
            return signer.update(data) + signer.finalize()
        except Exception as e:
            logging.error(f"Failed to sign data: {str(e)}")


class authentication:
    def __init__(self, signing_obj):
        self.signing_obj = signing_obj

    def sign_in(self, username, password):
        try:
            # Derive key using PBKDF2 with HMAC and SHA-256
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            salt = secrets.token_bytes(32)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=300000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            # Sign in using ECDSA signature
            signed_key = self.signing_obj.sign_data(key)
            return signed_key
        except Exception as e:
            logging.error(f"Failed to sign in: {str(e)}")

    def verify_signature(self, signature):
        try:
            # Verify ECDSA signature
            if not signature:
                logging.warning("Signature is empty")
                return False
            verifier = self.signing_obj.public_key_pem.verify(hashes.SHA256(), signature)
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            logging.error(f"Failed to verify signature: {str(e)}")


# Example usage
storage_obj = storage()
signing_obj = signing()
authentication_obj = authentication(signing_obj)

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
