import sys
from datetime import date
import logging.config
import mmap
import memory_profiler
import traceback
from logging.handlers import RotatingFileHandler
import psutil
import os
import configparser
import argparse
import atexit  # To ensure cleanup of resources on program exit.
import secrets
import base64
import hashlib

# Define named constants for permissions, buffer size limits and allocation units
BUFFER_SIZE_LIMIT = 1024 * 1024 * 100  # 100 MB buffer size limit
ALLOCATION_UNIT_LINUX = 4096
ALLOCATION_UNIT_WINDOWS = 8192

class FernetKeyManager:
    def __init__(self):
        self._fernet_keys = {}

    def get_fernet_key(self, key_id=None):
        if not key_id:
            # If no key id is provided, generate a new one and store it
            key_id = secrets.token_urlsafe(16)
            self._fernet_keys[key_id] = Fernet.generate_key()

            return key_id, self._fernet_keys[key_id]

        elif key_id in self._fernet_keys:
            return key_id, self._fernet_keys[key_id]

        else:
            # If an unknown key id is provided, generate a new one
            key_id = secrets.token_urlsafe(16)
            self._fernet_keys[key_id] = Fernet.generate_key()

            return key_id, self._fernet_keys[key_id]

class SecureKeyStorage(FernetKeyManager):
    def __init__(self):
        super().__init__()

    def get_fernet_key(self, key_id=None):
        # Generate a new Fernet key or retrieve an existing one
        return super().get_fernet_key(key_id)

def secure_buffer_generation(buffer_size, fernet_key_id):
    try:
        available_memory = psutil.virtual_memory().available

        # Ensure safe allocation using the nearest multiple of 4096 (for Linux) or 8192 (for Windows)
        import platform

        if platform.system() == "Linux":
            allocation_unit = ALLOCATION_UNIT_LINUX
        elif platform.system() == "Windows":
            allocation_unit = ALLOCATION_UNIT_WINDOWS

        buffer_size_limit = available_memory // allocation_unit * allocation_unit

        # Perform dynamic memory checks
        if buffer_size > BUFFER_SIZE_LIMIT:
            raise MemoryError(f"Buffer size {buffer_size} exceeds safe allocation limit of {BUFFER_SIZE_LIMIT}")

        # Generate a buffer
        buffer = hashlib.sha256(os.urandom(64)).digest()

        # Encrypt the buffer with Fernet
        fernet_key, key_id = SecureKeyStorage().get_fernet_key(fernet_key_id)
        encrypted_buffer = Fernet(fernet_key).encrypt(buffer)

        return encrypted_buffer, key_id
    except Exception as e:
        logging.error(f"Failed to generate buffer: {str(e)}")

def cleanup():
    try:
        # Clean up generated buffers
        for buffer in buffers:
            if hasattr(buffer, 'close'):
                buffer.close()

            del buffer

        # Remove configuration files and keys
        import os

        for file_path in [SecureKeyStorage().config_path]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)

                    logging.debug(f"Removed {file_path}")
                except Exception as e:
                    logging.error(f"Failed to remove {file_path}: {str(e)}")
    finally:
        pass

if __name__ == "__main__":
    atexit.register(cleanup)

try:
    main()
except PermissionError as e:
    # Handle permission errors differently
    logging.error(f"Permission denied when accessing {e.filename}: {str(e)}")

    try:
        cleanup()
    except Exception as e:
        logging.error(f"Cleanup failed after exception: {str(e)}")
except Exception as e:
    # Log exceptions before cleanup
    logging.error(f"Main execution failed: {str(e)}\n{traceback.format_exc()}")

    try:
        cleanup()
    except Exception as e:
        logging.error(f"Cleanup failed after exception: {str(e)}")

# Initialize Fernet for encryption and decryption operations
FERNET = Fernet(SecureKeyStorage().get_fernet_key()[1])
buffers = []
