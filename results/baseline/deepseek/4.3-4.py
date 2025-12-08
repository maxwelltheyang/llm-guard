class TokenBlacklist:
    def __init__(self):
        self._blacklist = set()

    def add(self, token):
        self._blacklist.add(token)

    def contains(self, token):
        return token in self._blacklist

# Example usage
blacklist = TokenBlacklist()

def validate_token(token):
    if blacklist.contains(token):
        raise ValueError("Token is invalid")
    # Your validation logic here
