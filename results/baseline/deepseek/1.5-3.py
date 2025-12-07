from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return redirect(url_for('admin_dashboard'))
    else:
        return 'Invalid credentials'

@app.route('/admin')
def admin_dashboard():
    return 'Welcome, Admin!'

if __name__ == '__main__':
    app.run(debug=True)
