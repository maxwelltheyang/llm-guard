import os
from typing import Optional, Dict
from pyelasticsearch import ElasticSearch
from cryptography.fernet import Fernet
from datetime import timedelta
from jwt import encode, decode
from logging.config import dictConfig
import schedule
import time
import threading
import hashlib
import bcrypt
import logging

# Logging configuration
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'level': 'INFO'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

# Establish Vault client
try:
    import hvac
    client = hvac.Client(url=os.environ['VAULT_ADDR'], token=os.environ['VAULT_TOKEN'])
except Exception as e:
    logging.error(f'Failed to establish Vault client: {e}')

class ElkConnectionCredentials:
    def __init__(self):
        self.elastic_username = os.environ.get('ELASTIC_USERNAME', None)
        self.elastic_password = os.environ.get('ELASTIC_PASSWORD', None)

    def get_credentials(self):
        return {'username': self.elastic_username, 'password': self.elastic_password}

class JwkReader:
    def __init__(self):
        self.jwk_secret_name = 'jwk'

    def read_jwk(self) -> str:
        try:
            return client.secrets.kv.read_secret(self.jwk_secret_name)['value']
        except Exception as e:
            logging.error(f'Failed to read JWK from Vault: {e}')
            raise

class JwtGenerator:
    def __init__(self, jwk_reader: JwkReader):
        self.jwk_reader = jwk_reader

    def generate_token(self, sub, aud, exp) -> str:
        try:
            # Generate JWT token using RS256 algorithm
            jwk = self.jwk_reader.read_jwk()
            payload = {
                'sub': sub,
                'aud': aud,
                'exp': exp
            }
            jwt_token = encode(payload, key=jwk, algorithm='RS256')
            return jwt_token
        except Exception as e:
            logging.error(f'Failed to generate JWT token: {e}')
            raise

class RotateElkCredentialsThread(threading.Thread):
    def __init__(self, rotate_elk_credentials_function):
        super().__init__()
        self.rotate_elk_credentials_function = rotate_elk_credentials_function
        self.lock = threading.Lock()

    def run(self):
        with self.lock:
            try:
                self.rotate_elk_credentials_function()
            except Exception as e:
                logging.error(f'Failed to rotate ELK credentials: {e}')

# Establish ELK connection using the ConnectionPool class
elk_connection_credentials = ElkConnectionCredentials()
try:
    elk_connection = ElasticSearch(url='https://localhost:9200', auth=(elk_connection_credentials.get_credentials()['username'], elk_connection_credentials.get_credentials()['password']))
except Exception as e:
    logging.error(f'Failed to establish ELK connection: {e}')

jwk_reader = JwkReader()
jwt_generator = JwtGenerator(jwk_reader)

# Schedule Vault token rotation every 30 days
rotate_elk_credentials_thread = RotateElkCredentialsThread(rotate_elk_credentials)
schedule.every(30).days.do(rotate_elk_credentials_thread.run)

while True:
    schedule.run_pending()
    time.sleep(1)
