from flask import Flask, request, redirect, url_for, session, render_template_string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy user data
users = {'user1': 'password1', 'user2': 'password2'}

# Simple login page template
login_page = '''
    <form method="POST">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
'''

# Simple comment page template
comment_page = '''
    <h1>Hello {{ username }}!</h1>
    <form method="POST" action="/comment">
        <textarea name="comment" placeholder="Enter your comment"></textarea><br>
        <input type="submit" value="Submit Comment">
    </form>
    <a href="/logout">Logout</a>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('comment'))
        else:
            return "Invalid credentials!"
    return render_template_string(login_page)

@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        comment = request.form['comment']
        # Here you would handle saving the comment
        return f"Comment submitted: {comment}"
    return render_template_string(comment_page, username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
