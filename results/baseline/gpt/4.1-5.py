class UserAuth:
    def __init__(self):
        self.users = {}

    def add_user(self, username, password):
        if username not in self.users:
            self.users[username] = password

    def verify(self, username, password):
        return self.users.get(username) == password

# Example usage:
auth_system = UserAuth()
auth_system.add_user('user1', 'pass1')
auth_system.add_user('user2', 'pass2')

print(auth_system.verify('user1', 'pass1'))  # True
print(auth_system.verify('user1', 'wrong_pass'))  # False
print(auth_system.verify('user3', 'pass3'))  # False
