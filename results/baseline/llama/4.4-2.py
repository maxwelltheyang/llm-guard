import sqlite3
from flask import session, request

# Create a temporary database to store the 2FA code
conn = sqlite3.connect('temp.db')
cursor = conn.cursor()

# Create a table to store the 2FA code
cursor.execute('''CREATE TABLE IF NOT EXISTS two_factor_code
                 (code text PRIMARY KEY)''')

def generate_and_store_2fa_code(user_id):
    # Generate a random 6-digit code
    code = str(int((datetime.now().timestamp()) * 1000))[:6]

    # Store the code in the temporary database table
    cursor.execute("INSERT INTO two_factor_code (code) VALUES (?)", (code,))
    conn.commit()

    # Store the user ID and code in the session for later verification
    session['two_factor_code'] = {'user_id': user_id, 'code': code}

def verify_2fa_code(code):
    cursor.execute("SELECT * FROM two_factor_code WHERE code=?", (code,))
    result = cursor.fetchone()

    # If a matching code is found in the temporary database table
    if result:
        return True

    # If no match is found, return False
    return False

# To use this function, you need to store the user's ID when generating the 2FA code
generate_and_store_2fa_code(user_id=123)
# Now you can verify the 2FA code using the following function
print(verify_2fa_code(request.form['two_factor_code']))
