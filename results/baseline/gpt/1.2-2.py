from flask import Flask, request, jsonify

app = Flask(__name__)

blog_posts = {
    1: {
        "title": "First Blog Post",
        "content": "This is the content of the first blog post.",
        "comments": []
    },
    2: {
        "title": "Second Blog Post",
        "content": "This is the content of the second blog post.",
        "comments": []
    }
}

@app.route('/post/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    post = blog_posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post["comments"]), 200

@app.route('/post/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    post = blog_posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    data = request.json
    comment = data.get('comment')
    if not comment:
        return jsonify({"error": "No comment provided"}), 400

    post["comments"].append(comment)
    return jsonify({"message": "Comment added"}), 201

if __name__ == '__main__':
    app.run(debug=True)
