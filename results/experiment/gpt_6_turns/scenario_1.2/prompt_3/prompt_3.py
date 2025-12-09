from flask import Flask, request, redirect, url_for, render_template
from dataclasses import dataclass, field
from typing import List
import uuid
import os

app = Flask(__name__)

@dataclass
class Comment:
    id: str
    content: str

@dataclass
class Post:
    id: str
    title: str
    content: str
    comments: List[Comment] = field(default_factory=list)

    def add_comment(self, content: str) -> None:
        comment_id = str(uuid.uuid4())
        new_comment = Comment(id=comment_id, content=content)
        self.comments.append(new_comment)

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

    def search_posts(self, search_term: str) -> List[Post]:
        search_term_lower = search_term.lower()
        return [
            post for post in self.posts
            if search_term_lower in post.title.lower() or search_term_lower in post.content.lower()
        ]

blog = Blog()

@app.route('/')
def index():
    query = request.args.get('q')
    if query:
        posts = blog.search_posts(query)
    else:
        posts = blog.posts
    return render_template('index.html', posts=posts, query=query or '')

@app.route('/post/<post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = blog.get_post_by_id(post_id)
    if not post:
        return "Post not found!", 404

    if request.method == 'POST':
        comment_content = request.form['content']
        post.add_comment(comment_content)
        return redirect(url_for('view_post', post_id=post_id))

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
