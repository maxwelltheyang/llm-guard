import time
from typing import Dict

class BruteForceProtection:
    def __init__(self):
        self.locked_users: Dict[str, int] = {}  # username/IP -> last_attempt_time
        self.max_attempts = 5
        self.timeout_minutes = 15

    def is_locked(self, username_or_ip: str) -> bool:
        if username_or_ip not in self.locked_users:
            return False
        return time.time() - self.locked_users[username_or_ip] < self.timeout_minutes * 60

    def increment_attempt(self, username_or_ip: str):
        if self.is_locked(username_or_ip):
            return
        self.locked_users[username_or_ip] = time.time()

    def check_brute_force(self, username_or_ip: str) -> int:
        self.increment_attempt(username_or_ip)
        attempts = len([t for t in self.locked_users.values() if t == self.locked_users[username_or_ip]])
        if attempts >= self.max_attempts:
            raise Exception(f"Brute force protection triggered for {username_or_ip}")
        return attempts

# Example usage
protection = BruteForceProtection()

def login(username, password):
    # Simulate a failed login attempt
    if username == 'locked_user':
        raise Exception("Invalid credentials")

    try:
        attempts = protection.check_brute_force(username)
        print(f"Failed login attempt {attempts} for user {username}")
    except Exception as e:
        if "Brute force protection triggered" in str(e):
            time.sleep(1 * 60)  # wait 1 minute to be locked out for at least one minute
            raise

login('locked_user', 'wrong_password')
