import sqlite3
import secrets
from typing import Optional

# Create an in-memory SQLite database for storing the 2FA code temporarily
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create a table to store the 2FA code
cursor.execute('''CREATE TABLE temp_2fa (code TEXT PRIMARY KEY)''')

# Generate a random 6-digit 2FA code and store it in the temporary database
def generate_2fa_code():
    return str(secrets.randbelow(10**6)).zfill(6)

stored_code = generate_2fa_code()
cursor.execute('INSERT INTO temp_2fa (code) VALUES (?)', (stored_code,))
conn.commit()

# Function to verify the 2FA code
def verify_2fa_code(user_input: str) -> bool:
    cursor.execute('SELECT code FROM temp_2fa WHERE code = ?', (user_input,))
    result = cursor.fetchone()
    return result is not None

# Example usage of the verification function
user_input = input("Enter your 2FA code: ")
if verify_2fa_code(user_input):
    print("Verification successful!")
else:
    print("Verification failed.")
