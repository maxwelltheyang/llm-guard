from secrets import choice
import string

# Define a custom character set including all letters (uppercase and lowercase), digits, and common punctuation symbols
custom_characters = string.ascii_letters + string.digits + "!@#$%^&*()_+{}[]|;:<>?,./\""

def generate_password(length=40):
    """Generate a random password of specified length using characters from the custom character set."""
    if not isinstance(length, int) or length <= 0:
        raise ValueError("Password length must be a positive integer.")

    password_candidates = [choice(custom_characters) for _ in range(length)]  # Generate a list of characters for the password
    return ''.join(password_candidates)  # Convert the list to a string and return the password

# Ensure secrets module is imported if not already done so
try:
    from secrets import choice
except ImportError:
    print("The 'secrets' module is required for generating secure passwords. Please install it.")
    exit(1)

def main():
    while True:
        try:
            length = int(input("Enter the desired password length (minimum 8 characters): "))
            if length < 8:
                raise ValueError("Password length must be at least 8 characters.")

            password = generate_password(length)
            print(f"Generated Password: {password}")
            break
        except ValueError as e:
            print(f"Invalid input. Please enter a positive integer greater than or equal to 8.\n{e}")

if __name__ == "__main__":
    main()
