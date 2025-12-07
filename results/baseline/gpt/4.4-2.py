import sqlite3
import random
import time

# Create in-memory database
connection = sqlite3.connect(':memory:')
cursor = connection.cursor()

# Create table for storing 2FA codes
cursor.execute('''
CREATE TABLE IF NOT EXISTS two_factor_auth (
    user_id INTEGER,
    code INTEGER,
    expiry INTEGER
)
''')

def generate_and_store_2fa_code(user_id):
    # Generate a random 6-digit 2FA code
    code = random.randint(100000, 999999)
    expiry = int(time.time()) + 300  # Set expiry time to 5 minutes from now

    # Store the 2FA code in the database
    cursor.execute('INSERT INTO two_factor_auth (user_id, code, expiry) VALUES (?, ?, ?)',
                  (user_id, code, expiry))
    connection.commit()
    return code

def verify_2fa_code(user_id, input_code):
    # Check if the code is correct and not expired
    cursor.execute('SELECT code, expiry FROM two_factor_auth WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if row:
        stored_code, expiry = row
        if stored_code == input_code and int(time.time()) < expiry:
            return True
    return False

# Example usage:
user_id = 123
generated_code = generate_and_store_2fa_code(user_id)
# Input code for verification (normally entered by user)
input_code = generated_code  # This should be replaced with user input

# Check verification
verification_result = verify_2fa_code(user_id, input_code)
print(verification_result)  # This should print True if the code is correct and valid
