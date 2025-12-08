import hashlib
import getpass

class User:
    def __init__(self, username, password):
        self.username = username
        self.password_hash = self.hash_password(password)

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def verify_password(cls, username, provided_password, stored_hash):
        if cls.get_user(username).password_hash == stored_hash:
            return True
        else:
            return False

    @classmethod
    def get_user(cls, username):
        # assume we have a dictionary of users for simplicity
        users = {'admin': User('admin', 'password')}
        return users.get(username)

def main():
    username = input("Enter your admin username: ")
    provided_password = getpass.getpass("Enter the password: ")

    stored_hash = User.get_user(username).password_hash
    if User.verify_password(username, provided_password, stored_hash):
        print("Password is correct")
    else:
        print("Incorrect password")

if __name__ == "__main__":
    main()
