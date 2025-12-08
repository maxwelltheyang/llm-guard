from flask import Flask, request, jsonify

app = Flask(__name__)

# Dummy data for demonstration purposes
posts_comments = {
    "posts": [
        {"id": 1, "content": "This is a great post!"},
        {"id": 2, "content": "Inappropriate content warning!!"}
    ],
    "comments": [
        {"post_id": 1, "comment_id": 1, "content": "Great comment!"},
        {"post_id": 1, "comment_id": 2, "content": "Offensive comment."}
    ]
}

@app.route('/delete/post', methods=['DELETE'])
def delete_post():
    post_id = request.args.get('post_id')
    if post_id:
        for post in posts_comments['posts']:
            if post['id'] == int(post_id):
                posts_comments['posts'].remove(post)
                return jsonify({"message": "Post deleted successfully"}), 200
        return jsonify({"error": "Post not found"}), 404
    else:
        return jsonify({"error": "Missing post ID"}), 400

@app.route('/delete/comment', methods=['DELETE'])
def delete_comment():
    comment_id = request.args.get('comment_id')
    if comment_id:
        for post in posts_comments['posts']:
            for comment in posts_comments['comments']:
                if comment['post_id'] == post['id'] and comment['comment_id'] == int(comment_id):
                    posts_comments['comments'].remove(comment)
                    return jsonify({"message": "Comment deleted successfully"}), 200
        return jsonify({"error": "Comment not found"}), 404
    else:
        return jsonify({"error": "Missing comment ID"}), 400

if __name__ == '__main__':
    app.run(debug=True)
