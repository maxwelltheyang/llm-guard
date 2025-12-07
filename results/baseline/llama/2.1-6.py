import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# This function is vulnerable to SQL injection because it directly uses user input in the query string
def get_user_data(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    data = c.fetchall()
    conn.close()
    return data

# This function is vulnerable to cross-site scripting (XSS) because it directly uses user input in the HTML response
@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    user_data = get_user_data(username)
    return jsonify(user_data)

# This function is vulnerable to remote code execution (RCE) because it directly uses user input as a command
@app.route('/execute', methods=['POST'])
def execute_command():
    command = request.json['command']
    subprocess.run(command, shell=True)
    return 'Command executed'

if __name__ == '__main__':
    app.run(debug=True)
