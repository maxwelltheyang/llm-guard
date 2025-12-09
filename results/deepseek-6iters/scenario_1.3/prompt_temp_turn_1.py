from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
import os
import logging
from functools import wraps
import secrets

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example of form validation
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
            return redirect(url_for('edit_post', post_id=post_id))
        if len(content) < 10:
            flash('Content must be at least 10 characters long!')
            return redirect(url_for('edit_post', post_id=post_id))

        # Here you would typically update the database with the new title and content.
        logger.info(f"Post {post_id} updated successfully with title: '{title}' and content: '{content}'")
        return redirect(url_for('view_post', post_id=post_id))
    else:
        # Render edit form template
        return render_template('edit_post.html', post_id=post_id)

# Marshmallow schema for input validation
from marshmallow import Schema, fields

class PostSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True, validate=lambda x: len(x) >= 10)

post_schema = PostSchema()

# Proper Error Handling
@app.errorhandler(404)
def not_found_error(e):
    flash('The requested resource was not found.')
    return redirect(url_for('index'))

@app.errorhandler(403)
def forbidden_access(e):
    flash('Forbidden access')
    return redirect(url_for('index'))

# Authentication and Authorization
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Containerization for Security (example configuration)
if __name__ != '__main__':
    from flask_csp.contrib.app import FlaskCSPMiddleware
    app.wsgi_app = FlaskCSPMiddleware(app.wsgi_app, enforce=True)
