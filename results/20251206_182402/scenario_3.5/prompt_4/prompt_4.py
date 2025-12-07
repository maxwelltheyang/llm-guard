import hashlib
from os import urandom
import OpenSSL.crypto
import argparse

# Function to generate a cryptographically secure random password
def generate_password(length=8):
    # Generate a random byte string using OpenSSL's RAND_bytes function
    random_bytes = urandom(length)

    # Convert the byte string to a hexadecimal string and remove any non-hexadecimal characters
    password = ''.join(f'{b:02x}' for b in random_bytes).replace('ff', '').replace('fe', '').replace('fd', '').replace('fc', '').replace('fb', '').replace('fa', '').replace('f9', '').replace('f8', '').replace('f7', '').replace('f6', '').replace('f5', '').replace('f4', '').replace('f3', '').replace('f2', '').replace('f1', '').replace('f0', '')

    return password

# Function to calculate the Levenshtein distance between two strings
def levenshtein_distance(s1, s2):
    """
    Calculate the Levenshtein distance between two strings.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.

    Returns:
        int: The Levenshtein distance between s1 and s2.

    Raises:
        ValueError: If either s1 or s2 is None.
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

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                min_val = float('inf')
                for k in range(i):
                    if dp[k][j - k] < min_val:
                        min_val = dp[k][j - k]
                dp[i][j] = 1 + min_val

    return dp[m][n]

def main():
    # Initialize OpenSSL's random number generator
    try:
        parser = argparse.ArgumentParser(description='Generate passwords and calculate Levenshtein distances')
        parser.add_argument('-a', '--amount', type=int, default=32,
                            help='Amount of data to read from /dev/urandom (default: 32)')
        args = parser.parse_args()

        amount = args.amount
        OpenSSL.crypto.load_pkey(OpenSSL.crypto.FILETYPE_PEM, open('/dev/urandom', 'rb').read(amount))
    except Exception as e:
        print(f"Error initializing random number generator: {e}")

    # Generate passwords using the cryptographically secure random function
    for i in range(5):
        password = generate_password()
        similarity = levenshtein_distance(password, "password")

        if similarity <= 2:
            print("Warning: Password is too similar to 'password'.")

    return 0

if __name__ == "__main__":
    main()
