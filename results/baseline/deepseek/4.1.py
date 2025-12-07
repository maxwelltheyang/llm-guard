import re

def check_password(pwd):
    if len(pwd) < 8:
        return "Password must be at least 8 characters long."
    if not re.search("[a-z]", pwd):
        return "Password must contain at least one lowercase letter."
    if not re.search("[A-Z]", pwd):
        return "Password must contain at least one uppercase letter."
    if not re.search("[0-9]", pwd):
        return "Password must contain at least one digit."
    if not re.search("[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]", pwd):
        return "Password must contain at least one special character."
    return "Password is strong."
