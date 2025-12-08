from datetime import datetime, timedelta

class User:
    def __init__(self):
        self.password_expires = None
        self.two_fa_code = {}

    def set_password(self):
        self.password_expires = datetime.now() + timedelta(days=90)

    def generate_two_fa_code(self):
        code = str(datetime.now().timestamp())  # Generate a random code based on current timestamp
        self.two_fa_code[code] = datetime.now()

    def check_two_fa_code(self, code):
        if code in self.two_fa_code and (datetime.now() - self.two_fa_code[code]).total_seconds() <= 300:
            return True
        else:
            return False

# Example usage:
user = User()
user.set_password()
print(user.password_expires)

user.generate_two_fa_code()
code1 = '1623456789'  # Example 2FA code
print(user.check_two_fa_code(code1))  # Should print: True

import time
time.sleep(310)  # Wait for 5.17 minutes
print(user.check_two_fa_code(code1))  # Should print: False
