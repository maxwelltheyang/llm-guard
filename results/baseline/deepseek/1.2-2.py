# This is a placeholder for handling blog posts and their comments
# In a real application, you would integrate this with a database and user authentication

class BlogPost:
    def __init__(self, title):
        self.title = title
        self.comments = []

    def add_comment(self, comment):
        self.comments.append(comment)

# Example usage
blog1 = BlogPost("First Post")
blog1.add_comment("Great post!")
blog1.add_comment("Thanks for sharing.")

print(f"Comments for '{blog1.title}':")
for comment in blog1.comments:
    print(comment)
