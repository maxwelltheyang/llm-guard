from flask import Flask, request, jsonify
import sqlite3
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length
import hashlib
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publication_date = db.Column(db.Date, nullable=False)

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128))

class LoginForm(FlaskForm):
    borrower_name = StringField('Borrower Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])

def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return jsonify({'error': 'Missing Authorization Header'}), 401
        # Implement authentication logic here using the auth header
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        borrower_name = form.borrower_name.data
        password = form.password.data
        # Hash and compare passwords
        borrower = Borrower.query.filter_by(name=borrower_name).first()
        if borrower is None:
            return jsonify({'error': 'Borrower not found'}), 404
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if borrower.password_hash == hashed_password:
            # Login successful, set authentication header
            auth_header = f'Bearer {hashed_password}'
            return jsonify({'message': 'Login successful', 'auth_header': auth_header}), 200
    else:
        return jsonify(form.errors), 400

@app.route('/book/<string:title>/borrow', methods=['POST'])
@requires_auth
def borrow_book(title):
    try:
        data = request.json
        borrower_name = data['borrower_name']

        book = Book.query.filter_by(title=title).first()
        if book is None:
            return jsonify({'error': 'Book not found'}), 404

        borrower = Borrower.query.filter_by(name=borrower_name).first()
        if borrower is None:
            return jsonify({'error': 'Borrower not found'}), 404

        book_borrower = BookBorrower(book_id=book.id, borrower_id=borrower.id, borrow_date='2023-01-01', return_date=None)
        db.session.add(book_borrower)
        db.session.commit()

        return jsonify({'message': 'Book borrowed successfully'}), 201
    except sqlite3.Error as e:
        print(e)
        return jsonify({'error': 'Database error'}), 500

@app.route('/book/<string:title>/return', methods=['POST'])
@requires_auth
def return_book(title):
    try:
        data = request.json
        borrower_name = data['borrower_name']

        book = Book.query.filter_by(title=title).first()
        if book is None:
            return jsonify({'error': 'Book not found'}), 404

        borrower = Borrower.query.filter_by(name=borrower_name).first()
        if borrower is None:
            return jsonify({'error': 'Borrower not found'}), 404

        book_borrower = BookBorrower.query.filter_by(book_id=book.id, borrower_id=borrower.id).first()
        if book_borrower is None:
            return jsonify({'error': 'Book borrow status not found'}), 404

        book_borrower.return_date = '2023-01-01'
        db.session.commit()

        return jsonify({'message': 'Book returned successfully'}), 200
    except sqlite3.Error as e:
        print(e)
        return jsonify({'error': 'Database error'}), 500

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', default=False)
    app.run(debug=debug_mode, threaded=True)

class BookBorrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey(Book.id))
    borrower_id = db.Column(db.Integer, db.ForeignKey(Borrower.id))
    borrow_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)

class BorrowerForm(FlaskForm):
    name = StringField('Borrower Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])

@app.route('/borrower', methods=['POST'])
def create_borrower():
    form = BorrowerForm()
    if form.validate_on_submit():
        borrower_name = form.name.data
        email = form.email.data
        phone_number = form.phone_number.data
        password = form.password.data

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        borrower = Borrower(name=borrower_name, email=email, phone_number=phone_number, password_hash=hashed_password)
        db.session.add(borrower)
        db.session.commit()

        return jsonify({'message': 'Borrower created successfully'}), 201
    else:
        return jsonify(form.errors), 400

@app.route('/borrower/<string:name>', methods=['GET'])
def get_borrower(name):
    borrower = Borrower.query.filter_by(name=name).first()
    if borrower is None:
        return jsonify({'error': 'Borrower not found'}), 404
    else:
        return jsonify({'name': borrower.name, 'email': borrower.email, 'phone_number': borrower.phone_number}), 200

@app.route('/book/<string:title>', methods=['GET'])
def get_book(title):
    book = Book.query.filter_by(title=title).first()
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    else:
        return jsonify({'title': book.title, 'author': book.author}), 200

if __name__ == '__main__':
    app.run(debug=True)
