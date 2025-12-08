import os
import sys
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

# Check for SQL Injection vulnerability
def check_sql_injection():
    with app.app_context():
        db.create_all()

        # Test SQL injection on a vulnerable endpoint
        @app.route('/test', methods=['POST'])
        def test_endpoint():
            query = request.form['query']
            results = db.session.execute(query)

            return str(results)

# Check for Cross-Site Scripting (XSS) vulnerability
def check_xss_vulnerability():
    with app.app_context():
        @app.route('/test', methods=['POST'])
        def test_endpoint():
            data = request.form['data']
            # Store the user input in a database or a variable
            return data

# Check for Cross-Site Request Forgery (CSRF) vulnerability
def check_csrf_vulnerability():
    with app.app_context():
        @app.route('/test', methods=['POST'])
        def test_endpoint():
            token = request.form['token']
            if token == 'expected_token':
                return 'Success!'

            # Return a 400 Bad Request response
            return 'Invalid token'

# Run the checks
check_sql_injection()
check_xss_vulnerability()
check_csrf_vulnerability()

app.run(debug=True)
