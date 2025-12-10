import hashlib
import binascii
from passlib.hash import argon2
import ast
import logging
import getpass  # For secure password entry

logging.basicConfig(level=logging.INFO)

def hash_password(password):
    """
    Hashes a password using Argon2.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: A string containing the hexadecimal representation of the hashed password and its parameters.
    """
    # Derive the key using Argon2
    try:
        time_cost = int(input("Enter time cost: "))
        if time_cost <= 1:
            logging.error(f"Invalid input for time cost: {time_cost}. Time cost must be greater than 1.")
            return None
    except ValueError as e:
        logging.error(f"Invalid input for time cost: {e}")
        return None

    try:
        memory_cost = int(input("Enter memory cost: "))
        if memory_cost < 65536:
            logging.error(f"Invalid input for memory cost: {memory_cost}. Memory cost must be at least 65536.")
            return None
    except ValueError as e:
        logging.error(f"Invalid input for memory cost: {e}")
        return None

    try:
        hash_function = input("Enter hash function (argon2, argon2i, argon2id): ")
        if hash_function not in ['argon2', 'argon2i', 'argon2id']:
            logging.error(f"Invalid hash function: {hash_function}. Supported hash functions are 'argon2', 'argon2i', and 'argon2id'.")
            return None
    except ValueError as e:
        logging.error(f"Invalid input for hash function: {e}")
        return None

    try:
        parallelism = int(input("Enter parallelism: "))
    except ValueError as e:
        logging.error(f"Invalid input for parallelism: {e}")
        return None

    parameters = argon2.using(hash_function, time_cost=time_cost, memory_cost=memory_cost, parallelism=parallelism).parameters()
    hashed_password = argon2.using(hash_function, **parameters).hash(password)

    # Return the hexadecimal representation of the hashed password and its parameters
    return binascii.hexlify(parameters['salt']) + ': ' + str(parameters) + ': ' + hashed_password

# Example usage:
password = getpass.getpass("Please enter your password: ")  # Secure password entry
hashed_password = hash_password(password)
if hashed_password is not None:
    print(hashed_password)

stored_hash_input = input("Enter the stored hash to verify against (in hexadecimal format): ")

def verify_password(stored_hash, provided_password):
    """
    Verifies a password against the stored hash.

    Args:
        stored_hash (str): The stored hashed password and its parameters.
        provided_password (str): The password to be verified.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    # Extract the parameters from the stored hash
    salt = binascii.unhexlify(stored_hash.split(': ')[0])
    parameters_str = stored_hash.split(': ')[1]
    parameters = ast.literal_eval(parameters_str)

    # Derive the new key using Argon2 with the original parameters
    new_hashed_password = argon2.using(**parameters).hash(provided_password)

    # Return True if the keys match, False otherwise
    return stored_hash.split(': ')[-1] == new_hashed_password

# Example usage:
if hashed_password is not None:
    print(verify_password(hashed_password, password))  # Should print: True
print(verify_password(stored_hash_input, "wrongpassword"))  # Should print: False
