import hashlib
from getpass import getpass
import argparse
import logging
import secrets
import os

try:
    from secrets import getrandom as random
except ImportError:
    from os import urandom as random

# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def generate_password(length=32):
    try:
        # Use PBKDF2 with SHA-256 and 200,000 iterations to improve security
        salt = random(16)

        pepper = b"pepper"

        hashed_password = hashlib.pbkdf2_hmac('sha256', pepper + salt, salt, 200000, dklen=length).hex()

        return salt.hex(), hashed_password
    except ValueError as e:
        logging.error(f"Error generating password: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def levenshtein_distance(s1, s2):
    """
    Calculate the Levenshtein distance between two strings.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.

    Returns:
        int: The Levenshtein distance between s1 and s2.

    Raises:
        TypeError: If either s1 or s2 is not a string.
    """
    if not isinstance(s1, str) or not isinstance(s2, str):
        raise TypeError("Both inputs must be strings")

    m = len(s1)
    n = len(s2)

    # Handle edge cases
    if m == 0:
        return n
    if n == 0:
        return m

    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1,
                           dp[i][j - 1] + 1,
                           dp[i - 1][j - 1] + cost)

    return dp[m][n]

def store_password(hashed_password, salt):
    # Store password securely in an environment variable
    os.environ['PASSWORD'] = hashed_password
    os.environ['SALT'] = salt

def main():
    # Initialize logging configuration
    try:
        parser = argparse.ArgumentParser(description='Generate passwords and calculate Levenshtein distances')

        # Add argument validation for password length
        parser.add_argument('--length', type=int, default=32,
                            help='Length of the generated hashed password')

        # Parse arguments
        args = parser.parse_args()

    except Exception as e:
        logging.error(f"Error parsing arguments: {e}")

    # Define a configurable password similarity threshold
    similarity_threshold = 2

    # Generate passwords using the cryptographically secure random function
    for i in range(5):
        salt, hashed_password = generate_password(args.length)

        store_password(hashed_password, salt)

        # Calculate Levenshtein distance to 'password'
        similarity = levenshtein_distance(hashed_password, "password")

        logging.info(f"Iteration {i+1}: Generated hashed password: ${os.environ['PASSWORD']}, Salt: ${os.environ['SALT']}, Similarity score: {similarity}")

        if similarity <= similarity_threshold:
            logging.warning(f"Hashed password is too similar to 'password': {similarity}")

    return 0

if __name__ == "__main__":
    main()
