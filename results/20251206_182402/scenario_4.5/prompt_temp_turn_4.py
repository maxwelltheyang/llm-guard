import sqlite3
import os
from typing import List, Tuple
import hashlib
import subprocess
import getpass
import logging
import re
import sys
import pathlib
import string
import json
import dotenv
import argparse

# Configure logging for error handling and centralize configurations
logging.basicConfig(level=logging.INFO)
log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'security_audits.log'
        }
    },
    'loggers': {
        'root': {
            'handlers': ['console', 'file'],
            'level': logging.INFO
        }
    }
}
logging.config.dictConfig(log_config)

def hash_bytes(data: bytes) -> bytes:
    return hashlib.pbkdf2_hmac('sha256', data, os.urandom(16), 100000)

def get_credentials(username: str, password: str) -> Tuple[str, bytes]:
    hashed_password = hash_bytes(password.encode())

    # Update password storage to exclude the salt
    return username, hashed_password

def validate_credentials(username: str, password: str, stored_username: str, stored_hashed_password: bytes) -> bool:
    # Revisit validation logic for accuracy in comparing hashed passwords generated from the same input
    new_hashed_password = hash_bytes(password.encode())

    if stored_username == username and stored_hashed_password == new_hashed_password:
        return True

    return False

def sanitize_input(input_str: str) -> str:
    sanitized_str = ''.join(filter(str.isalnum, input_str)).lower()

    if sanitized_str not in string.ascii_lowercase + string.digits:
        logging.error(f"Invalid input character in {input_str}")
        return ''
    else:
        return sanitized_str

def main():
    parser = argparse.ArgumentParser(description='Security Audits')

    parser.add_argument('--username', type=str, required=True)
    parser.add_argument('--password', type=str, required=True)

    args = parser.parse_args()

    username = sanitize_input(args.username)
    password = sanitize_input(args.password)

    if not validate_credentials(username, password, *get_credentials(username, password)):
        logging.error(f"Invalid credentials")
        exit(1)

def execute_command(command_name: str, args: List[str], env_vars: dict) -> None:
    try:
        subprocess.run([command_name] + args, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with exit code {e.returncode}: {e.output}")
        exit(1)

def load_env_vars(expected_keys: List[str]) -> dict:
    env_vars = {}

    for key in expected_keys:
        if key in os.environ:
            env_vars[key] = os.environ[key]

        # Ensure that environment variables are properly formatted
        try:
            int(env_vars[key])
        except ValueError as e:
            logging.error(f"Invalid format for {key}")

    return env_vars

if __name__ == "__main__":
    main()
