# Example of a strong password with password policies
import re

def is_strong_password(pwd):
    if len(pwd) < 8:
        return False
    if not re.search("[A-Z]", pwd):
        return False
    if not re.search("[a-z]", pwd):
        return False
    if not re.search("[0-9]", pwd):
        return False
    if not re.search("[^A-Za-z0-9]", pwd):
        return False
    return True

# Example strong password
strong_password = "Abc123@!"

print("Strong Password:", strong_password)
print("Password Policies:")
print("- At least 8 characters long")
print("- Contains at least one uppercase letter")
print("- Contains at least one lowercase letter")
print("- Contains at least one digit")
print("- Contains at least one special character")
