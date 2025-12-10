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
from cryptography.fernet import Fernet
import secrets
import base64
import hashlib

# Define named constants for permissions, buffer size limits and hash sizes
BUFFER_SIZE_LIMIT_PERMISSIONS = 0o600
MAX_SAFE_ALLOC_SIZE = psutil.virtual_memory().total / 2  # In bytes
HASH_SHA256_BLOCK_SIZE = 60

class SecureKeyStorage:
    def __init__(self):
        self.config_path = "config.ini"

    def load_config(self, permission_error=False):
        try:
            if not os.access(self.config_path, os.R_OK):
                raise PermissionError(f"Permission denied when reading {self.config_path}")

            config = configparser.ConfigParser()

            config.read(self.config_path)

            return config
        except Exception as e:
            if permission_error:
                raise

            logging.error(f"Failed to load configuration from {self.config_path}: {str(e)}")

            try:
                cleanup()
            except Exception as e:
                logging.error(f"Cleanup failed after exception: {str(e)}")

def validate_config(config):
    critical_sections = ["Encryption", "Cleanup"]

    for section in config.sections():
        if section not in critical_sections:
            continue

        for key, value in config[section].items():
            try:
                # Attempt to decode as an encryption key
                Fernet(value).encrypt(b"example")

                logging.debug(f"{section}::{key}: {value} appears to be a valid encryption key")
            except Exception as e:
                logging.error(f"Invalid encryption key in {section}::{key}: {str(e)}")

def secure_buffer_generation(buffer_size):
    try:
        available_memory = psutil.virtual_memory().available

        # Ensure safe allocation using the nearest multiple of 4096 (for Linux) or 8192 (for Windows)
        import platform

        if platform.system() == "Linux":
            allocation_unit = 4096
        elif platform.system() == "Windows":
            allocation_unit = 8192

        buffer_size_limit = available_memory // allocation_unit * allocation_unit

        # Perform dynamic memory checks
        if buffer_size > buffer_size_limit:
            raise MemoryError(f"Buffer size {buffer_size} exceeds safe allocation limit of {buffer_size_limit}")

        buffer = hashlib.sha256(os.urandom(HASH_SHA256_BLOCK_SIZE)).digest()

        return Fernet(SecureKeyStorage().get_fernet_key()).encrypt(buffer)
    except Exception as e:
        logging.error(f"Failed to generate buffer: {str(e)}")

def cleanup():
    try:
        # Clean up generated buffers
        for buffer in buffers:
            if hasattr(buffer, 'close'):
                buffer.close()

            del buffer

        # Remove configuration files
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

try:
    validate_config(SecureKeyStorage().load_config(permission_error=True))
except PermissionError as e:
    # Handle permission errors differently
    logging.error(f"Permission denied when reading configuration file: {str(e)}")
