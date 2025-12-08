password = "Giraff3#LemonTree$Pineapple"

print("Password:", password)

# Password policy examples:
# - Length: Minimum 12 characters, maximum 128 characters
# - Complexity: At least one uppercase letter (A-Z), at least one lowercase letter (a-z),
#   at least one digit (0-9), and at least one special character (!, @, #, etc.)
# - Uniqueness: Passwords should be unique for each user or account

print("Password policy:")
print("Length:", len(password))
print("Uppercase letters:", any(char.isupper() for char in password))
print("Lowercase letters:", any(char.islower() for char in password))
print("Digits:", any(char.isdigit() for char in password))
print("Special characters:", any(not char.isalnum() for char in password))
