class BlogPost:
    def __init__(self, title, content):
        self.title = title
        self.content = content

class Blog:
    def __init__(self):
        self.posts = []

    def add_post(self, post):
        self.posts.append(post)

    def search_by_title(self, query):
        return [post for post in self.posts if query.lower() in post.title.lower()]

    def search_by_content(self, query):
        return [post for post in self.posts if query.lower() in post.content.lower()]

# Example usage:
blog = Blog()
blog.add_post(BlogPost("Hello World", "This is a sample blog post"))
blog.add_post(BlogPost("Goodbye World", "Another example blog post"))

print(blog.search_by_title("World"))  # Search by title
print(blog.search_by_content("sample"))  # Search by content
