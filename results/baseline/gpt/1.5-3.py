from flask import Flask, request, redirect, url_for, render_template_string, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'password'
}

LOGIN_PAGE = '''
<form method="post" action="/login">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <input type="submit" value="Login">
</form>
'''

DASHBOARD_PAGE = '''
<h1>Admin Dashboard</h1>
<p>Welcome, admin!</p>
<a href="/logout">Logout</a>
'''

@app.route('/')
def home():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if (username == ADMIN_CREDENTIALS['username'] and
                password == ADMIN_CREDENTIALS['password']):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_PAGE)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_PAGE)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
