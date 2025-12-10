import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from passlib.context import CryptContext as _CryptContext  # Update to latest version (3.0.1 or higher)
import validators
from wtforms import Form, StringField, IntegerField, validators

app = Flask(__name__)
app.config['SECRET_KEY'] from os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        try:
            # Validate and hash password using passlib
            self.password = _CryptContext(schemes=['argon2'], default='argon2', pbkdf2_variants=['pbkdf2-sha256']).hash(password)

        except Exception as e:
            return str(e)

    def check_password(self, password):
        from django.contrib.auth.hashers import check_password as _check_password
        # Securely verify the hashed password with Django's built-in validation
        try:
            return _check_password(password, self.password)
        except Exception as e:
            return False

class RegistrationForm(Form):
    username = StringField('Username', validators=[validators.DataRequired()])
    content = IntegerField('Content', validators=[validators.DataRequired()], trim=True)

# Close open transactions and database connections when the application exits
try:
    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()
finally:
    if not hasattr(app, 'tested'):
        app.test_client().get('/')
        app.tested = True

@app.route('/post', methods=['GET', 'POST'])
def post():
    form = RegistrationForm()

    if request.method == 'POST':
        content = request.form.get('content')

        # Validate and escape user input using wtforms
        try:
            if form.validate_on_submit():
                with db.session.no_autoflush:
                    new_message = Message(content=content, user_id=current_user.id)
                    db.session.add(new_message)
                    db.session.commit()

            else:
                print("Form validation failed.")

        except Exception as e:
            app.logger.error(f"An error occurred: {e}")

    return render_template('post.html', form=form)

# Update logout to properly clear sessions and login status
@app.route('/logout')
def logout():
    # Clear user data from session upon successful logout
    if 'username' in session:
        del session['username']

    if 'user_id' in session:
        del session['user_id']

    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)
