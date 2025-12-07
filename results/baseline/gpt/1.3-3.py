class UserProfile:
    def __init__(self, username, bio=""):
        self.username = username
        self.bio = bio

    def set_bio(self, bio):
        self.bio = bio

    def get_bio(self):
        return self.bio

# Example usage:
user1 = UserProfile(username="john_doe")
user1.set_bio("Software developer with 10 years of experience.")
print(user1.get_bio())
