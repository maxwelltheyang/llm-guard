import os

def clean_up_deployment(secret_key_file):
    if os.path.exists(secret_key_file):
        os.remove(secret_key_file)
    print("Secret key file deleted.")

def clean_ci_environment():
    env_vars = ["CI_ENV_VAR1", "CI_ENV_VAR2", "CI_ENV_VAR3"]  # Replace with actual CI env vars
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
    print("CI environment cleaned.")

# Example use
clean_up_deployment('path/to/secret_key_file')
clean_ci_environment()
