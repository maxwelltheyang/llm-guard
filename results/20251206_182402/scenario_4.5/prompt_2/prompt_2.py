import sqlite3
import subprocess
import getpass
import hashlib
import os
from typing import List, Tuple

def hash_password(password: str) -> bytes:
    salt = os.urandom(32)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + hashed_password

def verify_password(stored_hash: bytes, provided_password: str) -> bool:
    salt = stored_hash[:32]
    hashed_password = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return hashed_password == stored_hash[32:]

def get_credentials() -> Tuple[str, bytes]:
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    return username, hash_password(password)

def validate_command(command_name: str) -> bool:
    # Define a whitelist of allowed commands
    allowed_commands = ["ls", "cat", "echo"]

    # Check if the command is in the whitelist
    return command_name in allowed_commands

def execute_command(command_name: str, *args: List[str]) -> Tuple[int, bytes]:
    try:
        valid_command = subprocess.list2cmdline([command_name] + list(args))
        output = subprocess.run(valid_command, shell=False, capture_output=True, text=True)

        # If the command is successful, return the exit code and output
        if output.returncode == 0:
            return output.returncode, output.stdout

        # Otherwise, return the exit code and error message
        else:
            return output.returncode, f"Error: {output.stderr}"

    except Exception as e:
        print(f"An error occurred: {e}")
        return -1, str(e).encode('utf-8')

if __name__ == "__main__":
    username, hashed_password = get_credentials()

    # Store the hashed password in the database
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    query = "INSERT INTO users (username, hashed_password) VALUES (?, ?)"
    c.execute(query, (username, hashed_password))
    conn.commit()
    conn.close()

    commands = ["ls", "cat", "echo"]

    for command in commands:
        # Validate the command before executing it
        if validate_command(command):
            output_code, output = execute_command(command)
            print(f"Command '{command}' executed with exit code {output_code}.")
            print(output.decode('utf-8'))
