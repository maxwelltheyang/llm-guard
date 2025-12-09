from flask import Flask, request, render_template
from .models import Post, db  # Import your models and db configuration
import os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Use environment variables for configuration settings
app.config['DEBUG'] = bool(os.getenv('FLASK_DEBUG', default=False))

# Configure logging for production environments
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask-Blog startup')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return "Please provide a search term in the query parameter.", 400

    # Perform a case-insensitive search on title and content fields
    posts = Post.query.filter(
        (Post.title.ilike(f'%{query}%')) | (Post.content.ilike(f'%{query}%'))
    ).all()

    return render_template('search_results.html', posts=posts, query=query)

if __name__ == '__main__':
    app.run()
