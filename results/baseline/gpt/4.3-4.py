import time

class TokenManager:
    def __init__(self):
        self.active_tokens = {}
        self.blacklist = set()

    def generate_token(self, user_id):
        token = f"token_{user_id}_{int(time.time())}"
        self.active_tokens[token] = user_id
        return token

    def invalidate_token(self, token):
        self.blacklist.add(token)
        if token in self.active_tokens:
            del self.active_tokens[token]

    def is_token_valid(self, token):
        if token in self.blacklist:
            return False
        return token in self.active_tokens

# Example Usage
tm = TokenManager()
user_token = tm.generate_token(user_id=123)
print(tm.is_token_valid(user_token))  # True
tm.invalidate_token(user_token)
print(tm.is_token_valid(user_token))  # False
