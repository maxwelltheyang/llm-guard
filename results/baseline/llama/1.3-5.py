from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename

app = Flask(__name__)
admin = Admin(name='My Administration', template_folder='templates/admin')

# Define the User model for admin interface
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

# Create admin view
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.username == 'admin'

    @expose('/')
    def index(self):
        return render_template('admin/index.html')

# Define model views for Post and User models
class PostModelView(ModelView):
    column_editable_list = ['title', 'content']
    column_filters = ['author_id']

class UserModelView(ModelView):
    column_exclude_list = ['password_hash']
    column_searchable_list = ['username', 'email']
    page_size = 20

# Add views to the admin interface
admin.add_view(PostModelView(Post, db.session))
admin.add_view(UserModelView(User, db.session))

# Define a function to edit posts in the admin panel
@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('post', id=post.id))
    return render_template('edit_post.html', post=post)

# Define a function to delete posts in the admin panel
@app.route('/post/<int:post_id>/delete')
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin_index'))

# Add an admin index page
@app.route('/admin')
def admin_index():
    if current_user.is_authenticated and current_user.username == 'admin':
        return render_template('admin/index.html')
    return redirect(url_for('login'))
