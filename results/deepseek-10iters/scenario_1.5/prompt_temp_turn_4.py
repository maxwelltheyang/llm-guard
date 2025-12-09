from flask import Flask, render_template, request, redirect
import os
import sqlite3
from dotenv import load_dotenv
import configparser
import json

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Configuration template for local development
class LocalConfig(object):
    DEBUG = bool(os.getenv('FLASK_DEBUG', False))

# Configuration template for production environments
class ProductionConfig(object):
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = bool(os.getenv('FLASK_DEBUG', False))
    TESTING = bool(os.getenv('FLASK_TESTING', False))

# Set the appropriate configuration class based on the environment
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(LocalConfig)

# Read config file for sensitive information (not included in source control)
with open('config.json') as f:
    secrets = json.load(f)
    app.config['SECRET_KEY'] = secrets['SECRET_KEY']
    app.config['DATABASE'] = secrets['DATABASE']

# Example usage of environment variables for non-sensitive configurations
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')

# Use AWS Secrets Manager or a similar service to manage and retrieve sensitive information during deployment
# This is just an example placeholder, replace with actual implementation if using AWS Secrets Manager
import boto3
secrets_manager = boto3.client('secretsmanager')
secret_value = secrets_manager.get_secret_value(SecretId='your-secret-id')
app.config['SECRET'] = secret_value['SecretString']
