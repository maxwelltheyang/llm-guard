from flask import Flask, render_template, request, redirect, url_for, jsonify
import secrets
from passlib.context import CryptContext
from django.contrib.auth.password_validation import validate_password  # Import the validator
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
# Use environment variables for database credentials
import os
db_url = 'postgresql://'+os.environ['DB_USERNAME']+':'+os.environ['DB_PASSWORD']+'@localhost:'+os.environ['DB_PORT']+'/'+os.environ['DB_NAME']
engine = create_engine(db_url)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    @staticmethod
    def validate_password(password):
        try:
            validate_password(password)  # Validate passwords
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error validating password: {e}")
            raise

def hash_password(password):
    pwd_context = CryptContext(schemes=["pbkdf2"], default="pbkdf2_sha256_64")
    return pwd_context.hash(password)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            session = Session()
            user = session.query(User).filter_by(username=username).first()  # Validate the username
            if not user or not hash_password(password) == user.password_hash:  
                return 'Invalid username or password', 401
            token = secrets.token_urlsafe(16)
            user.token = token  # Update the token in the database
            session.commit()
            return jsonify({'token': token})
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error logging in: {e}")
            return "An error occurred while logging in", 500
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    try:
        token = request.args.get('token')  # Retrieve the token from the client-side
        if not token:
            return 'No authentication token provided'
        session = Session()
        user = session.query(User).filter_by(token=token).first()  # Validate the token on the server-side
        if not user:
            return 'Invalid authentication token', 401
        try:
            posts = text("SELECT * FROM posts WHERE author_id = :user_id").params(user_id=user.id)
            results = engine.execute(posts)
            post_list = []
            for row in results:
                post = {'id': row['id'], 'title': row['title'], 'content': row['content']}
                post_list.append(post)
            return render_template('dashboard.html', posts=post_list)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error retrieving dashboard: {e}")
            return "An error occurred while retrieving the dashboard", 500
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error accessing dashboard: {e}")
        return "An error occurred while accessing the dashboard", 500

if __name__ == '__main__':
    app.run(debug=False)
