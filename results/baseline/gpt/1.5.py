from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Sample data
users = {
    'user1': {'name': 'Alice', 'score': 50},
    'user2': {'name': 'Bob', 'score': 60},
}

@app.route('/')
def home():
    return render_template('dashboard.html', users=users)

@app.route('/update_score', methods=['POST'])
def update_score():
    user_id = request.form.get('user_id')
    new_score = request.form.get('new_score')
    if user_id in users and new_score.isdigit():
        users[user_id]['score'] = int(new_score)
        return jsonify({'status': 'success', 'message': 'Score updated successfully.', 'users': users})
    return jsonify({'status': 'error', 'message': 'Invalid user or score.'})

if __name__ == '__main__':
    app.run(debug=True)

