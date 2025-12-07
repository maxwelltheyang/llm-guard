import getpass
import hashlib
import sqlite3

# Create a new SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create table for users
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users
    (username TEXT PRIMARY KEY, password TEXT)
''')

# Function to register new user
def register():
    username = input('Enter a unique username: ')
    while True:
        password = getpass.getpass('Enter a password: ')
        confirm_password = getpass.getpass('Confirm your password: ')
        if password == confirm_password:
            break
        print('Passwords do not match. Please try again.')

    # Hash the password before storing it in the database
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Insert new user into the users table
    cursor.execute("INSERT INTO users VALUES (?, ?)", (username, hashed_password))
    conn.commit()

# Function to login existing user
def login():
    username = input('Enter your username: ')
    password = getpass.getpass('Enter your password: ')

    # Retrieve the stored hash of the user's password from the database
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    hashed_password = cursor.fetchone()

    if hashed_password is None:
        print('Username not found.')
        return

    # Compare the provided password with the stored hash
    if hashlib.sha256(password.encode()).hexdigest() == hashed_password[0]:
        print('Login successful!')
    else:
        print('Incorrect password.')

# Menu for user to choose between registration and login
while True:
    print('\nChoose an option:')
    print('1. Register a new account')
    print('2. Login to existing account')
    choice = input('> ')

    if choice == '1':
        register()
    elif choice == '2':
        login()
    else:
        print('Invalid choice.')

# Close the database connection
conn.close()
