from flask import Flask, render_template, request, redirect, url_for, flash, current_app, logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
import os

# Load environment variables for the application configuration
if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

# Define a custom module for password validation
# Removed unnecessary import

class RegistrationForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$",
                          message="Password should contain at least 1 uppercase letter, "
                                  "1 lowercase letter, 1 digit and special character.")
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data)
            # Validate password
            validate_password(form.password.data, user.__dict__)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Password does not meet the requirements: {e}')
    return render_template('register.html', form=form)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error with logging"""
    app.logger.warning('Page Not Found: %s', e)  
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Return a custom 500 error with logging"""
    app.logger.critical('Internal Server Error: %s', e)  
    return render_template('500.html'), 500

# Log user deletion
@app.route('/delete-user/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        app.logger.error(f'User deletion failed: {e}')  
        flash(f'User deletion failed')

if __name__ == '__main__':
    # Disable debug mode for production security
    app.run(debug=False)
