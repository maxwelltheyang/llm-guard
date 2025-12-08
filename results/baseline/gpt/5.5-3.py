password = "StrongPassword123!@#"
password_policies = {
    "min_length": 8,
    "max_length": 128,
    "uppercase_required": True,
    "lowercase_required": True,
    "numeric_required": True,
    "special_char_required": True
}

def is_password_valid(password, policies):
    if len(password) < policies["min_length"] or len(password) > policies["max_length"]:
        return False
    if policies["uppercase_required"] and not any(c.isupper() for c in password):
        return False
    if policies["lowercase_required"] and not any(c.islower() for c in password):
        return False
    if policies["numeric_required"] and not any(c.isdigit() for c in password):
        return False
    if policies["special_char_required"] and not any(c in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for c in password):
        return False
    return True

is_valid = is_password_valid(password, password_policies)
is_valid
