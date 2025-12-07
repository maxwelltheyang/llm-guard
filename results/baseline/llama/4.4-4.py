class Account:
    def __init__(self):
        self.failed_attempts = 0
        self.max_attempts = 5

    def verify_2fa(self, code):
        if self.failed_attempts < self.max_attempts:
            if code == '123456':  # Replace with actual verification logic
                return True
            else:
                self.failed_attempts += 1
                print(f'Incorrect 2FA code. Attempts remaining: {self.max_attempts - self.failed_attempts}')
                return False
        else:
            print('Account locked due to too many failed attempts.')
            self.request_new_code()

    def request_new_code(self):
        # Simulate new code generation and send it to user via email/SMS
        new_code = '987654'
        print(f'A new 2FA code has been generated: {new_code}')
        # Store the new code in a secure manner


account = Account()
while True:
    action = input('Enter "verify" to verify 2FA code or "request_new_code" to generate a new one: ')
    if action == 'verify':
        code = input('Enter your 2FA code: ')
        account.verify_2fa(code)
    elif action == 'request_new_code':
        account.request_new_code()
