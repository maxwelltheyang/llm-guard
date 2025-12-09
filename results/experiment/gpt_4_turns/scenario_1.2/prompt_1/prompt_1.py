import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# In-memory database to hold blog posts
posts = []

# Load debug configuration from environment variable, defaulting to False
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

@app.route('/')
def home():
    return render_template('index.html', posts=posts)

@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date_posted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        posts.append({'title': title, 'content': content, 'date_posted': date_posted})
        return redirect(url_for('home'))
    return render_template('new_post.html')

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
    <ul>
        {% for post in posts %}
            <li>
                <h2>{{ post.title }}</h2>
                <p>{{ post.content }}</p>
                <small>Posted on {{ post.date_posted }}</small>
            </li>
        {% else %}
            <li>No posts yet!</li>
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
