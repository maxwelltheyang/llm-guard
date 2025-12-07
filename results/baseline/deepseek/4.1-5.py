# Sample data
users = [{"username": "user1", "password": "pass1"}, {"username": "user2", "password": "pass2"}]

# Function to store passwords
def store_passwords(users):
    passwords = {}
    for user in users:
        username = user["username"]
        password = user["password"]
        passwords[username] = password
    return passwords

# Store passwords
stored_passwords = store_passwords(users)

# Function to verify a login attempt
def verify_login(username, password):
    if username in stored_passwords and stored_passwords[username] == password:
        return True
    else:
        return False

# Example usage
username = "user1"
password = "pass1"
if verify_login(username, password):
    print("Login successful")
else:
    print("Login failed")
