import bcrypt
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from django.contrib.auth.password_validation import validate_password
import re

# Database setup and model definition here...

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    def set_password(self, password):
        # Validate the password using Django's validate_password
        validate_password(password, user=self)
        # Hash and store the password securely
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Function to add a user with strong password validation
def add_user(username, password, session):
    try:
        new_user = User(username=username)
        new_user.set_password(password)
        session.add(new_user)
        session.commit()
    except SQLAlchemyError as e:
        print(f"An error occurred while adding user: {e}")
        session.rollback()
        raise  # Re-raise the exception to be handled by the caller if needed

# Example usage
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)
session = Session()
add_user('testuser', 'StrongPass123!', session)
