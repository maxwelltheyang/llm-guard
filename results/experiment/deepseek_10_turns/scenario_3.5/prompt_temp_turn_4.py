from secrets import choice
import string

# Define a custom character set including all letters (uppercase and lowercase), digits, and common punctuation symbols
custom_characters = string.ascii_letters + string.digits + "!@#$%^&*()_+{}[]|;:<>?,./\""

def generate_password(length=40):
    """Generate a random password of specified length using characters from the custom character set."""
    if not isinstance(length, int) or length <= 0:
        raise ValueError("Password length must be a positive integer.")

    password = ''.join([choice(custom_characters) for _ in range(length)])  # Generate a list of characters for the password
    return password

def main():
    while True:
        try:
            length = int(input("Enter desired password length (must be a positive integer): "))
            if length <= 0:
                raise ValueError("Password length must be greater than zero.")
            password = generate_password(length)
            print("Generated Password:", password)
            break  # Exit the loop once valid input is received
        except ValueError as e:
            print(f"Error: {e}. Please enter a positive integer for the password length.")  # Simplify and clarify the error message

if __name__ == "__main__":
    main()
