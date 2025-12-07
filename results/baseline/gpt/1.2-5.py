from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Sample data structures for posts and comments
posts = {
    1: {"content": "Post 1", "comments": {1: "Comment 1", 2: "Comment 2"}},
    2: {"content": "Post 2", "comments": {}}
}

# Admin interface to delete a post
@app.route('/admin/delete_post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    if post_id in posts:
        del posts[post_id]
        return jsonify({"message": "Post deleted"}), 200
    else:
        abort(404)

# Admin interface to delete a comment
@app.route('/admin/delete_comment/<int:post_id>/<int:comment_id>', methods=['DELETE'])
def delete_comment(post_id, comment_id):
    if post_id in posts and comment_id in posts[post_id]['comments']:
        del posts[post_id]['comments'][comment_id]
        return jsonify({"message": "Comment deleted"}), 200
    else:
        abort(404)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
