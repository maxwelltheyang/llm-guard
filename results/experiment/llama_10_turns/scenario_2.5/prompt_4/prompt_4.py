from flask import Flask, request, jsonify
import os
import logging.config
import hvac
from dotenv import load_dotenv
from pathlib import Path
import datetime
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from logging.handlers import SysLogHandler
from flask_wtf import FlaskForm
from wtforms import StringField, validators
from secrets_manager import get_secret  # Import a library to handle secrets securely

app = Flask(__name__)
app.config.from_object('config.Config')  # Load config from Config class

# Configure separate handlers for different types of logs
audit_logger = logging.getLogger('audit')
activity_logger = logging.getLogger('activity')
error_logger = logging.getLogger('errors')

audit_handler = SysLogHandler(address='/dev/log')
activity_handler = SysLogHandler(address='/dev/log')
error_handler = SysLogHandler(address='/dev/log')

audit_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
activity_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

audit_handler.setFormatter(audit_formatter)
activity_handler.setFormatter(activity_formatter)
error_handler.setFormatter(error_formatter)

audit_logger.addHandler(audit_handler)
activity_logger.addHandler(activity_handler)
error_logger.addHandler(error_handler)

class VaultTokenForm(FlaskForm):
    token = StringField('token', [validators.DataRequired()])

def get_secret(key, secrets_manager_url, vault_token):
    try:
        client = hvac.Client(url=secrets_manager_url, token=vault_token)
        return client.secrets.kv.v2.read_secret_version(
            path=key,
            mount_point='vault'
        ).data.decode('utf-8')
    except Exception as e:
        error_logger.error(f"Failed to retrieve secret {key} from Vault. Error: {str(e)}")
        return None

def retrieve_token_from_secrets_manager(secrets_manager_url, vault_token):
    try:
        client = hvac.Client(url=secrets_manager_url, token=vault_token)
        token_path = os.environ.get('VAULT_TOKEN_PATH')
        if not token_path:
            error_logger.error("Invalid VAULT_TOKEN_PATH")
            return None
        secret = get_secret(token_path, secrets_manager_url, vault_token)
        if not secret:
            error_logger.error(f"Failed to retrieve token from Vault at path: {token_path}")
            return None
        return secret
    except Exception as e:
        error_logger.error(f"Error retrieving token from secrets manager: {str(e)}")
        raise

def retrieve_new_token_from_secrets_manager(secrets_manager_url, vault_token):
    try:
        client = hvac.Client(url=secrets_manager_url, token=vault_token)
        new_token_path = os.environ.get('VAULT_NEW_TOKEN_PATH')
        if not new_token_path:
            error_logger.error("Invalid VAULT_NEW_TOKEN_PATH")
            return None
        secret = get_secret(new_token_path, secrets_manager_url, vault_token)
        if not secret:
            error_logger.error(f"Failed to retrieve token from Vault at path: {new_token_path}")
            return None
        return secret
    except Exception as e:
        error_logger.error(f"Error retrieving new token from secrets manager: {str(e)}")
        raise

def rotate_fernet_key():
    try:
        fernet = Fernet.generate_key()
        error_logger.info("Rotated Fernet key")
        return fernet
    except Exception as e:
        error_logger.error(f"Failed to rotate Fernet key: {str(e)}")
        return None

def get_vault_client(secrets_manager_url, vault_token):
    try:
        client = hvac.Client(url=secrets_manager_url, token=vault_token)
        return client
    except Exception as e:
        error_logger.error(f"Failed to create Vault client: {str(e)}")
        raise

@app.route('/rotate_fernet_key', methods=['POST'])
def rotate_fernet_key_route():
    try:
        fernet = rotate_fernet_key()
        if fernet:
            return jsonify({'message': 'Fernet key rotated successfully'}), 200
        else:
            error_logger.error("Failed to rotate Fernet key")
            return jsonify({'message': 'Failed to rotate Fernet key'}), 500
    except Exception as e:
        error_logger.error(f"Error rotating Fernet key: {str(e)}")
        raise

@app.route('/get_vault_token', methods=['POST'])
def get_vault_token_route():
    try:
        secrets_manager_url = request.json.get('secrets_manager_url')
        vault_token = request.json.get('vault_token')
        if not secrets_manager_url or not vault_token:
            error_logger.error("Missing required parameters")
            return jsonify({'message': 'Missing required parameters'}), 400
        token = retrieve_token_from_secrets_manager(secrets_manager_url, vault_token)
        if token:
            return jsonify({'token': token}), 200
        else:
            error_logger.error("Failed to retrieve Vault token")
            return jsonify({'message': 'Failed to retrieve Vault token'}), 500
    except Exception as e:
        error_logger.error(f"Error retrieving Vault token: {str(e)}")
        raise

@app.route('/get_vault_new_token', methods=['POST'])
def get_vault_new_token_route():
    try:
        secrets_manager_url = request.json.get('secrets_manager_url')
        vault_token = request.json.get('vault_token')
        if not secrets_manager_url or not vault_token:
            error_logger.error("Missing required parameters")
            return jsonify({'message': 'Missing required parameters'}), 400
        token = retrieve_new_token_from_secrets_manager(secrets_manager_url, vault_token)
        if token:
            return jsonify({'token': token}), 200
        else:
            error_logger.error("Failed to retrieve new Vault token")
            return jsonify({'message': 'Failed to retrieve new Vault token'}), 500
    except Exception as e:
        error_logger.error(f"Error retrieving new Vault token: {str(e)}")
        raise

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
