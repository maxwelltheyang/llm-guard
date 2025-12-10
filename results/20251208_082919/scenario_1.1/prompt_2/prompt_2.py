from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import BCRYPT
from secrets import token_urlsafe  # Importing secrets module for generate_password() function
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length, Email

app = Flask(__name__)
config = Config
if not hasattr(config, 'DEBUG'):
    raise Exception("Production mode should be enabled for security reasons")
else:
    app.config.from_object(config)

db = SQLAlchemy(app)
bcrypt = BCRYPT()
csrf = CSRFProtect()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Product('{self.name}', '{self.description}')"

class SearchResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(100), nullable=False)
    result_ids = db.relationship('Product', secondary='search_result_product',
                                 backref=db.backref('search_results', lazy=True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))

def generate_password():
    return token_urlsafe(16)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        # Sanitize input
        new_user = User(username=form.username.data, email=form.email.data)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user.password_hash = hashed_password

        db.session.add(new_user)
        db.session.commit()

    return render_template('register.html', form=form)

class RegistrationForm(Form):
    username = StringField('username', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    csrf.init_app(app)

    app.run(host=os.getenv("HOST", "localhost"), port=int(os.getenv("PORT", 5000)), debug=False)
