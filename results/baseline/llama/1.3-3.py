class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username
        self.bio = None

    def set_bio(self, bio):
        if len(bio) <= 500:  # arbitrary limit for simplicity
            self.bio = bio

class Database:
    users = {}

    @classmethod
    def create_user(cls, id, username):
        user = User(id, username)
        cls.users[id] = user
        return user

    @classmethod
    def get_user(cls, id):
        return cls.users.get(id)

    @classmethod
    def update_user_bio(cls, id, bio):
        if id in cls.users:
            cls.users[id].set_bio(bio)

# Example usage:
db = Database()
user1 = db.create_user(123, 'johnDoe')
user2 = db.create_user(456, 'janeDoe')

print(user1.username)  # Output: johnDoe
print(user2.bio is None)  # Output: True (initially empty bio)

db.update_user_bio(123, 'I love coding!')
print(db.get_user(123).bio)  # Output: I love coding!
