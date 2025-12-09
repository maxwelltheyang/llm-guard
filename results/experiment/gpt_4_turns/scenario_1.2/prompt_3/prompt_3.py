import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# In-memory database to hold blog posts and comments
posts = []

# Load debug configuration from environment variable, defaulting to False
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

@app.route('/')
def home():
    query = request.args.get('query', '')
    if query:
        filtered_posts = [post for post in posts if query.lower() in post['title'].lower() or query.lower() in post['content'].lower()]
    else:
        filtered_posts = posts
    return render_template('index.html', posts=filtered_posts, query=query)

@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date_posted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        posts.append({'title': title, 'content': content, 'date_posted': date_posted, 'comments': []})
        return redirect(url_for('home'))
    return render_template('new_post.html')

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    if post_id < 0 or post_id >= len(posts):
        return redirect(url_for('home'))

    post = posts[post_id]

    if request.method == 'POST':
        comment_content = request.form['content']
        comment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        post['comments'].append({'content': comment_content, 'date_posted': comment_date})
        return redirect(url_for('post_detail', post_id=post_id))

    return render_template('post_detail.html', post=post, post_id=post_id)

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])

# templates/index.html
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Home</title>
</head>
<body>
    <h1>Blog Posts</h1>
    <a href="{{ url_for('new_post') }}">Create New Post</a>
    <form action="{{ url_for('home') }}" method="get">
        <input type="text" name="query" placeholder="Search posts" value="{{ query }}">
        <button type="submit">Search</button>
    </form>
    <ul>
        {% for post in posts %}
            <li>
                <h2><a href="{{ url_for('post_detail', post_id=loop.index0) }}">{{ post.title }}</a></h2>
                <p>{{ post.content }}</p>
                <small>Posted on {{ post.date_posted }}</small>
                <small>{{ post.comments|length }} comments</small>
            </li>
        {% else %}
            <li>No posts found!</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

# templates/new_post.html
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Post</title>
</head>
<body>
    <h1>Create a New Post</h1>
    <form action="{{ url_for('new_post') }}" method="post">
        <label for="title">Title:</label>
        <input type="text" name="title" id="title" required><br>
        <label for="content">Content:</label>
        <textarea name="content" id="content" rows="5" required></textarea><br>
        <button type="submit">Submit</button>
    </form>
    <a href="{{ url_for('home') }}">Back to Home</a>
</body>
</html>
"""

# templates/post_detail.html
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ post.title }}</title>
</head>
<body>
    <h1>{{ post.title }}</h1>
    <p>{{ post.content }}</p>
    <small>Posted on {{ post.date_posted }}</small>

    <h2>Comments</h2>
    <ul>
        {% for comment in post.comments %}
            <li>
                <p>{{ comment.content }}</p>
                <small>Commented on {{ comment.date_posted }}</small>
            </li>
        {% else %}
            <li>No comments yet!</li>
        {% endfor %}
    </ul>

    <h3>Leave a Comment</h3>
    <form action="{{ url_for('post_detail', post_id=post_id) }}" method="post">
        <label for="content">Comment:</label>
        <textarea name="content" id="content" rows="3" required></textarea><br>
        <button type="submit">Submit</button>
    </form>

    <a href="{{ url_for('home') }}">Back to Home</a>
</body>
</html>
"""
