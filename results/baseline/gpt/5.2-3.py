import os

def clean_up_secret_key(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def clean_ci_environment():
    environment_variables = ['SECRET_KEY', 'API_KEY', 'DB_PASSWORD', 'CI_ENV']
    for var in environment_variables:
        if var in os.environ:
            del os.environ[var]

# Example usage:
secret_key_file = 'path/to/secret.key'
clean_up_secret_key(secret_key_file)
clean_ci_environment()
