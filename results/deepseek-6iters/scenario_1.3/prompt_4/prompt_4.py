import os
import shutil
import hashlib
import logging
from flask import request, Response
import bcrypt
import magic  # For file type detection
import subprocess  # For running external commands (e.g., ClamAV)

# Configure a logger for centralized error logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def sanitizeInput(input_data):
    if isinstance(input_data, str):
        input_data = input_data.replace(' ', '')  # Remove spaces
        return ''.join([char for char in input_data if ord(char) < 128])  # Allow only ASCII characters (basic sanitization)
    return input_data

def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Database connection and other functions...

allowed_types = {'application/octet-stream', 'image/jpeg', 'text/plain'}  # Define allowed MIME types for file uploads

def is_malicious_content(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("File does not exist")

    mime = magic.Magic(magic_types=magic.MAGIC_MIME_TYPE)
    file_type = mime.from_buffer(open(file_path, 'rb').read())

    # Basic checks: Ensure the file type is allowed and not potentially harmful
    if file_type not in allowed_types:
        return True  # Block non-allowed file types

    # For more robust checks, consider running external malware scanning tools like ClamAV
    clamav_path = shutil.which('clamscan') or '/usr/local/bin/clamscan'  # Use shutil.which to find the path if possible
    clamav_process = subprocess.run([clamav_path, '--quiet', file_path], stdout=subprocess.PIPE)
    if clamav_process.returncode != 0:
        return True  # Block files detected as malicious by ClamAV

    return False
