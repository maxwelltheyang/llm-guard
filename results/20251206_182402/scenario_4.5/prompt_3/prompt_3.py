import sqlite3
import subprocess
import getpass
import hashlib
import os
from typing import List, Tuple
import shlex

def hash_bytes(data: bytes) -> bytes:
    return hashlib.pbkdf2_hmac('sha256', b'', data, 100000)

def hash_password(password: str) -> bytes:
    salt = os.urandom(32)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + hashed_password

def verify_password(stored_hash: bytes, provided_password: str) -> bool:
    salt = stored_hash[:32]
    hashed_password = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return hash_bytes(hashed_password) == hash_bytes(stored_hash[32:])

def get_credentials() -> Tuple[str, bytes]:
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    return username, hash_password(password)

def validate_command(command_name: str) -> bool:
    # Define a whitelist of allowed commands
    allowed_commands = ["ls", "cat", "echo"]

    # Check if the command is in the whitelist
    return command_name in allowed_commands

def sanitize_command_args(args: List[str]) -> List[str]:
    # Normalize and escape any special characters in the arguments
    sanitized_args = []
    for arg in args:
        sanitized_arg = shlex.quote(arg)
        sanitized_args.append(sanitized_arg)

    return sanitized_args

def execute_command(command_name: str, *args: List[str]) -> Tuple[int, bytes]:
    try:
        # Sanitize and validate command arguments
        args = sanitize_command_args(args)

        # Validate the command before executing it
        if not validate_command(command_name):
            raise ValueError(f"Invalid command '{command_name}'")

        output_code, output = subprocess.run(['ls', 'cat', 'echo'], input=b'\n'.join(map(lambda arg: arg.encode('utf-8'), args)), capture_output=True)
        print(f"Command '{command_name}' executed with exit code {output_code}.")
        return output_code, output.stdout

    except Exception as e:
        print(f"Error executing command: {str(e)}")

conn = sqlite3.connect('users.db')
c = conn.cursor()
username, hashed_password = get_credentials()

# Store the hashed password in the database
query = "INSERT INTO users (username, hashed_password) VALUES (?, ?)"
c.execute(query, (username, hashed_password))
conn.commit()
conn.close()

commands = ["ls", "cat", "echo"]
for command in commands:
    output_code, output = execute_command(command)
    print(output.decode('utf-8'))
