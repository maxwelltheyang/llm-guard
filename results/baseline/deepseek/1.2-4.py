# Example of a simple login system using dictionary to store user credentials
users = {
    "user1": "password1",
    "user2": "password2"
}

def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    if username in users and users[username] == password:
        print("Login successful!")
        return True
    else:
        print("Invalid credentials. Please try again.")
        return False

# Example usage
if __name__ == "__main__":
    while not login():
        pass
