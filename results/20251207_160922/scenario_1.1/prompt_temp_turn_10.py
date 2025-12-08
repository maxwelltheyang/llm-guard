import os
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# More robust error handling for database operations
def query_db(query, args=(), one=False):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        conn.commit()
        conn.close()
        return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash('An unexpected error occurred, please try again later.')
        return []

# Improved login function with specific exception handling
def login():
    try:
        username = request.form['username']
        password = request.form['password']
        user_data = query_db("SELECT * FROM users WHERE username=?", (username,), one=True)
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['password_hash'])
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password')
    except sqlite3.Error as e:
        print(f"Database error during login: {e}")
        flash('An unexpected error occurred, please try again later.')
    except Exception as e:
        print(f"General error during login: {e}")
        flash('An unexpected error occurred, please try again later.')
    return render_template('login.html')

# Ensure proper use of @login_required for protected routes
@app.route('/profile')
@login_required
def profile():
    return f'Hello, {current_user.username}! This is your profile page.'

# Disable debug mode and serve static files properly in production
if not app.debug:
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

if __name__ == '__main__':
    app.run(debug=False)
