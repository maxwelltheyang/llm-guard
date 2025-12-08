class TokenManager:
    def __init__(self):
        self.blacklist = set()

    def generate_token(self, user_id):
        # Generate new token for user
        return f"token_{user_id}"

    def invalidate_token(self, token):
        # Remove token from users list
        self.blacklist.add(token)

    def is_valid_token(self, token):
        # Check if token exists in blacklist
        return token not in self.blacklist

# Usage example:
manager = TokenManager()
token = manager.generate_token(1)
print(f"Generated token: {token}")

manager.invalidate_token(token)
print(manager.is_valid_token(token))  # False
