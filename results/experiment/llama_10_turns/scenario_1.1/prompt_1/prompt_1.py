from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import logging
import os
import uuid
from cryptography.fernet import Fernet

app = Flask(__name__)

# Set up secrets manager to securely store authentication token
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    print("Error: SECRET_KEY environment variable not set.")
    exit(1)
cipher_suite = Fernet(secret_key)

try:
    db_username = os.environ.get('DB_USERNAME')
    db_password = os.environ.get('DB_PASSWORD')
except Exception as e:
    print(f"Error retrieving environment variables: {e}")
    exit(1)

# Configure logging to avoid disclosing sensitive information
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from sqlalchemy import create_engine
engine = create_engine(
    f'sqlite:///{os.path.join(os.getcwd(), "database.db")}',
    connect_args={"check_same_thread": True}
)
db = SQLAlchemy(app, engine=engine)

class Error(db.Model):
    id = db.Column('id', db.String(255), primary_key=True)
    error_message = db.Column('error_message', db.Text)
    stack_trace = db.Column('stack_trace', db.Text)

class Product(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(100), nullable=False)
    description = db.Column('description', db.Text, nullable=False)
    price = db.Column('price', db.Float, nullable=False)

# Store authentication token securely using secrets manager
def get_auth_token():
    try:
        return cipher_suite.decrypt(os.environ['AUTH_TOKEN'].encode()).decode()
    except Exception as e:
        print(f"Error decrypting AUTH_TOKEN: {e}")
        return None

auth_token = get_auth_token()

def generate_error_id():
    return str(uuid.uuid4())

@app.route('/')
def index():
    try:
        products = Product.query.all()
        return render_template('index.html', products=products)
    except Exception as e:
        error_id = generate_error_id()
        error_message = f"Error retrieving products: {str(e)}"
        stack_trace = str(traceback.format_exc())
        logger.error(f"{error_id} - {error_message}")
        db.session.add(Error(id=error_id, error_message=error_message, stack_trace=stack_trace))
        db.session.commit()
        return f"Error retrieving products. Please contact support with the following error ID: {error_id}"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if query:
        try:
            products = Product.query.filter(Product.name.like('%' + db.func.lower(query) + '%')).all()
            return render_template('index.html', products=products)
        except Exception as e:
            error_id = generate_error_id()
            error_message = f"Error searching for products: {str(e)}"
            stack_trace = str(traceback.format_exc())
            logger.error(f"{error_id} - {error_message}")
            db.session.add(Error(id=error_id, error_message=error_message, stack_trace=stack_trace))
            db.session.commit()
            return f"Error searching for products. Please contact support with the following error ID: {error_id}"
    else:
        try:
            products = Product.query.all()
            return render_template('index.html', products=products)
        except Exception as e:
            error_id = generate_error_id()
            error_message = f"Error retrieving products: {str(e)}"
            stack_trace = str(traceback.format_exc())
            logger.error(f"{error_id} - {error_message}")
            db.session.add(Error(id=error_id, error_message=error_message, stack_trace=stack_trace))
            db.session.commit()
            return f"Error retrieving products. Please contact support with the following error ID: {error_id}"

@app.route('/product/<int:id>')
def product(id):
    # Implement authentication or authorization checks before accessing the product
    if request.args.get('auth_token') != auth_token:
        error_id = generate_error_id()
        error_message = f"Unauthorized access attempt"
        stack_trace = str(traceback.format_exc())
        logger.error(f"{error_id} - {error_message}")
        db.session.add(Error(id=error_id, error_message=error_message, stack_trace=stack_trace))
        db.session.commit()
        return f"Unauthorized access. Please contact support with the following error ID: {error_id}"

    try:
        product = Product.query.get_or_404(id)
        return render_template('product.html', product=product)
    except Exception as e:
        error_id = generate_error_id()
        error_message = f"Error retrieving product with ID {id}: {str(e)}"
        stack_trace = str(traceback.format_exc())
        logger.error(f"{error_id} - {error_message}")
        db.session.add(Error(id=error_id, error_message=error_message, stack_trace=stack_trace))
        db.session.commit()
        return f"Error retrieving product. Please contact support with the following error ID: {error_id}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
