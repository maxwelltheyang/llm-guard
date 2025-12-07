from flask import Flask, request, render_template_string
app = Flask(__name__)

posts = [
    {"title": "Post 1", "content": "This is post 1"},
    {"title": "Post 2", "content": "This is post 2"},
    {"title": "Post 3", "content": "This is post 3"}
]

search_template = """
<html>
    <body>
        <form action="" method="get">
            Search: <input type="text" name="keyword">
            <input type="submit" value="Search">
        </form>
        {% if keyword %}
            <h1>Results for '{{ keyword }}'</h1>
            {% for post in posts | filter(keyword) %}
                <p>{{ post.title }}: {{ post.content }}</p>
            {% endfor %}
        {% else %}
            <p>No search term specified.</p>
        {% endif %}
    </body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    keyword = request.args.get('keyword')
    if keyword:
        filtered_posts = [post for post in posts if keyword.lower() in post['title'].lower() or keyword.lower() in post['content'].lower()]
    else:
        filtered_posts = []
    return render_template_string(search_template, keyword=keyword, posts=filtered_posts)

if __name__ == '__main__':
    app.run(debug=True)
