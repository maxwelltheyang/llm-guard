from datetime import datetime, timedelta
from collections import defaultdict

class BruteForceProtection:
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.locked_out = {}

    def add_failed_attempt(self, identifier):
        # Remove old attempts
        self.failed_attempts[identifier] = [
            time for time in self.failed_attempts[identifier]
            if time > datetime.now() - timedelta(minutes=15)
        ]
        # Add new attempt
        self.failed_attempts[identifier].append(datetime.now())

        # Check if should lock out
        if len(self.failed_attempts[identifier]) >= 5:
            self.locked_out[identifier] = datetime.now() + timedelta(minutes=15)

    def is_locked_out(self, identifier):
        if identifier in self.locked_out:
            if self.locked_out[identifier] > datetime.now():
                return True
            else:
                del self.locked_out[identifier]
                del self.failed_attempts[identifier]
        return False

# Usage
protection = BruteForceProtection()
identifier = "user_or_ip"

protection.add_failed_attempt(identifier)  # Log a failed attempt
locked = protection.is_locked_out(identifier)  # Check if locked out
