import secrets
import string

def generate_password():
    # Define character sets
    uppercase_letters = string.ascii_uppercase
    lowercase_letters = string.ascii_lowercase
    digits = string.digits
    special_chars = string.punctuation

    # Combine all characters into one set
    all_characters = uppercase_letters + lowercase_letters + digits + special_chars

    # Generate an 40-character password (or more) to improve entropy and diversity
    while True:
        password_candidates = [secrets.choice(all_characters) for _ in range(40)]
        if (any(c in uppercase_letters for c in password_candidates) and
            any(c in lowercase_letters for c in password_candidates) and
            any(c in digits for c in password_candidates) and
            any(c in special_chars for c in password_candidates)):
            break

    # Shuffle the list to potentially improve distribution of character types
    secrets.SystemRandom().shuffle(password_candidates)
    password = ''.join(password_candidates)
    return password

# Example usage:
if __name__ == "__main__":
    print(generate_password())
