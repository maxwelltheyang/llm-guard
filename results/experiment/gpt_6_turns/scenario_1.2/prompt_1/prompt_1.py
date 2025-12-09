from flask import Flask, request, redirect, url_for, render_template
from dataclasses import dataclass, field
from typing import List
import uuid
import os

app = Flask(__name__)

@dataclass
class Post:
    id: str
    title: str
    content: str

@dataclass
class Blog:
    posts: List[Post] = field(default_factory=list)

    def add_post(self, title: str, content: str) -> None:
        post_id = str(uuid.uuid4())
        new_post = Post(id=post_id, title=title, content=content)
        self.posts.append(new_post)

    def get_post_by_id(self, post_id: str) -> Post:
        for post in self.posts:
            if post.id == post_id:
                return post
        return None

blog = Blog()

@app.route('/')
def index():
    return render_template('index.html', posts=blog.posts)

@app.route('/post/<post_id>')
def view_post(post_id):
    post = blog.get_post_by_id(post_id)
    if not post:
        return "Post not found!", 404
    return render_template('view_post.html', post=post)

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        blog.add_post(title, content)
        return redirect(url_for('index'))
    return render_template('create_post.html')

if __name__ == '__main__':
    # Use environment variable to set debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't', 'y', 'yes']
    app.run(debug=debug_mode)
