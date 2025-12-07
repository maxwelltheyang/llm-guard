def search_posts(blog_posts, query):
    results = []
    for post in blog_posts:
        if query in post['title'] or query in post['content']:
            results.append(post)
    return results
