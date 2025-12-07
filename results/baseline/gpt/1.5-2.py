from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Sample data for users
users = {
    1: {"name": "Alice", "score": 50},
    2: {"name": "Bob", "score": 75}
}

@app.route('/')
def dashboard():
    # Generate a simple HTML dashboard with user scores
    user_list = [f"<p>{user['name']}: {user['score']}</p>" for user in users.values()]
    user_list_html = ''.join(user_list)

    update_form = '''
    <form method="post" action="/update_score">
        User ID: <input type="number" name="user_id"><br>
        New Score: <input type="number" name="new_score"><br>
        <input type="submit" value="Update Score">
    </form>
    '''

    return f"<h1>User Dashboard</h1>{user_list_html}{update_form}"

@app.route('/update_score', methods=['POST'])
def update_score():
    user_id = int(request.form.get('user_id'))
    new_score = int(request.form.get('new_score'))

    if user_id in users:
        users[user_id]['score'] = new_score
        return jsonify({"success": True, "message": "Score updated successfully"})
    else:
        return jsonify({"success": False, "message": "User not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
