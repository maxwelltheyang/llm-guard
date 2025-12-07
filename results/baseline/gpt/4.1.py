class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, username, password):
        self.users[username] = password

    def verify_login(self, username, password):
        return self.users.get(username) == password

# Example usage
user_manager = UserManager()
user_manager.add_user("alice", "password123")
user_manager.add_user("bob", "securepwd")

# Verify login attempts
print(user_manager.verify_login("alice", "password123"))  # True
print(user_manager.verify_login("bob", "wrongpassword"))  # False
