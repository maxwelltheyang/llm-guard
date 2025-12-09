from django.core.exceptions import ValidationError
from django.core.validators import validate_password
from django.db import models
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=256)

    def set_password(self, raw_password):
        validate_password(raw_password)  # Ensure the password is validated before setting it
        self.password_hash = generate_password_hash(raw_password, method='pbkdf2:sha256', salt_length=16)
