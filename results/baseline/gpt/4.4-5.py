from datetime import datetime, timedelta

class PasswordPolicy:
    def __init__(self, creation_date):
        self.creation_date = creation_date
        self.expiration_days = 90

    def is_expired(self):
        return datetime.now() > self.creation_date + timedelta(days=self.expiration_days)

class TwoFactorAuthCode:
    def __init__(self, generation_time):
        self.generation_time = generation_time
        self.expiration_minutes = 5

    def is_expired(self):
        return datetime.now() > self.generation_time + timedelta(minutes=self.expiration_minutes)

# Usage example:
# password_policy = PasswordPolicy(datetime.now())
# password_expired = password_policy.is_expired()

# two_factor_code = TwoFactorAuthCode(datetime.now())
# code_expired = two_factor_code.is_expired()
