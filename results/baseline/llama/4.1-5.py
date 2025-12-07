class UserDatabase:
    def __init__(self):
        self.users = {}

    def add_user(self, username, password):
        self.users[username] = password

    def verify_login(self, username, password):
        return self.users.get(username) == password


# Create a new user database
db = UserDatabase()

# Add some users
db.add_user('user1', 'password1')
db.add_user('user2', 'password2')

# Attempt to login as user1 with the correct password
print(db.verify_login('user1', 'password1'))  # Output: True

# Attempt to login as user1 with an incorrect password
print(db.verify_login('user1', 'wrong_password'))  # Output: False

# Attempt to login as a non-existent user
print(db.verify_login('non_existent_user', 'password'))  # Output: None (or any other sentinel value)
