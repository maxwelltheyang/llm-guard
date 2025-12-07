from datetime import datetime, timedelta
from typing import Dict, Set

class TokenManager:
    def __init__(self):
        self.active_tokens: Dict[str, datetime] = {}
        self.blacklisted_tokens: Set[str] = set()

    def generate_token(self, user_id: str) -> str:
        token = f"token_for_{user_id}_{datetime.utcnow().timestamp()}"
        self.active_tokens[token] = datetime.utcnow() + timedelta(hours=1)
        return token

    def invalidate_token(self, token: str):
        if token in self.active_tokens:
            del self.active_tokens[token]
        self.blacklisted_tokens.add(token)

    def is_token_valid(self, token: str) -> bool:
        if token in self.blacklisted_tokens:
            return False
        expiry_date = self.active_tokens.get(token)
        if not expiry_date:
            return False
        if datetime.utcnow() > expiry_date:
            self.invalidate_token(token)
            return False
        return True

    def logout(self, token: str):
        self.invalidate_token(token)

# Example usage:
# token_manager = TokenManager()
# token = token_manager.generate_token('user123')
# print(token_manager.is_token_valid(token))
# token_manager.logout(token)
# print(token_manager.is_token_valid(token))
