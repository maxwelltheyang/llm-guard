from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
from django.contrib.auth.password_validation import validate_password as dpw_validate_password

app = Flask(__name__)
if os.environ.get('FLASK_ENV') == 'development':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
else:
    # Replace with your production database URI
    pass
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/register', methods=['POST'])
def register():
    try:
        dpw_validate_password(request.form.get('password'))
        new_user = User(username=request.form.get('username'), password=request.form.get('password'))
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return "Invalid password", 400
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False if os.environ.get('FLASK_ENV') != 'development' else True)
