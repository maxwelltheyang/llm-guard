import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'secret'

# Connect to the SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create table for users if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (username text PRIMARY KEY, password text)''')

# Function to check login credentials
def check_login(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone() is not None

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Store the new user in the database
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return "User created successfully!"
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_login(username, password):
            # Login successful, store the username in session
            session['logged_in'] = True
            return "Login successful!"
        else:
            return "Invalid credentials"
    return render_template('login.html')

# Route to protect comments from anonymous users
@app.route('/comment', methods=['POST'])
def comment():
    if 'logged_in' in session and session['logged_in']:
        # Comment is allowed only for logged-in users
        username = session['username']
        comment_text = request.form['comment']
        print(f"{username} commented: {comment_text}")
        return "Comment posted successfully!"
    else:
        return "You must login to comment"

# Route to handle logout
@app.route('/logout')
def logout():
    # Remove the 'logged_in' session variable
    session.pop('logged_in', None)
    return "Logged out successfully!"

if __name__ == '__main__':
    app.run(debug=True)

# Protect route /comment using login_required decorator (simple implementation)
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
