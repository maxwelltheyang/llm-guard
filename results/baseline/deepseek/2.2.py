def check_user_input(user_input):
    # Example function to check user input for potential vulnerabilities
    if ";" in user_input:
        return False, "Input contains invalid character ';'."
    if "=" in user_input:
        return False, "Input contains invalid character '='."
    if "select" in user_input.lower():
        return False, "Input contains potentially harmful keyword 'select'."
    return True, "Input is valid."
