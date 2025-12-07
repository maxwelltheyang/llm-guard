import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@app.before_request
def check_vulnerabilities():
    # Check for SQL injection vulnerabilities
    if request.args.get('username') and request.args.get('password'):
        query = User.query.filter_by(username=request.args.get('username'), password=request.args.get('password'))
        result = query.first()

        if result:
            return jsonify({'message': 'Authorized'}), 200

    # Check for Cross-Site Scripting (XSS) vulnerabilities
    if request.method == 'POST':
        data = request.get_json()
        if 'username' in data and 'password' in data:
            user = User(username=data['username'], password=data['password'])
            db.session.add(user)
            db.session.commit()

    # Check for Cross-Site Request Forgery (CSRF) vulnerabilities
    if request.method == 'POST':
        token = request.headers.get('X-CSRF-Token')
        if not token:
            return jsonify({'message': 'Missing CSRF Token'}), 401

if __name__ == '__main__':
    app.run(debug=True)
