class TwoFactorAuthSystem:
    def __init__(self, max_attempts):
        self.max_attempts = max_attempts
        self.current_attempts = 0
        self.code = None
        self.locked = False

    def generate_code(self):
        if self.locked:
            raise ValueError("Account is locked. Request a new code.")
        self.code = "123456"  # In practice, generate a random code
        self.current_attempts = 0
        self.locked = False
        return self.code

    def verify_code(self, input_code):
        if self.locked:
            raise ValueError("Account is locked. Request a new code.")

        if self.code is None:
            raise ValueError("No code generated. Request a new code.")

        if input_code == self.code:
            self.current_attempts = 0
            self.code = None
            return True
        else:
            self.current_attempts += 1
            if self.current_attempts >= self.max_attempts:
                self.locked = True
            return False

# Example Usage
auth_system = TwoFactorAuthSystem(max_attempts=3)
auth_system.generate_code()      # User requests a code
auth_system.verify_code("654321") # Incorrect code
auth_system.verify_code("654321") # Incorrect code
auth_system.verify_code("654321") # Incorrect code
auth_system.generate_code()      # Requesting new code after lock
