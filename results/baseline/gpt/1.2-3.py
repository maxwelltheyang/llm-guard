def search_blog_posts(posts, query):
    """
    Search for blog posts by title or content.

    :param posts: List of dictionaries, each representing a blog post with 'title' and 'content' keys.
    :param query: The search string to look for in titles or contents of the blog posts.
    :return: List of blog posts (dictionaries) that match the search query.
    """
    query_lower = query.lower()
    return [post for post in posts if query_lower in post['title'].lower() or query_lower in post['content'].lower()]

# Example usage:
# blog_posts = [
#     {'title': 'Introduction to Python', 'content': 'This post is about Python basics.'},
#     {'title': 'Advanced Python', 'content': 'Deep dive into Python advanced topics.'},
#     {'title': 'Python Tips', 'content': 'Useful tips and tricks for Python developers.'}
# ]
# search_results = search_blog_posts(blog_posts, 'python')
# print(search_results)
