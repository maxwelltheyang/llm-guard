# This script is intended to review a Dockerfile for common security best practices and potential vulnerabilities.
# It's important to note that this is a simplified example and may not cover all aspects of Docker image security.

import subprocess

def check_dockerfile():
    try:
        # Run a static analysis tool like hadolint (if available) or custom rules for Dockerfile linting
        result = subprocess.run(['hadolint', 'Dockerfile'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Security issues found in Dockerfile:")
            print(result.stderr)
        else:
            print("No security issues found.")
    except FileNotFoundError:
        print("Hadolint is not installed. Please install it to run the Docker image security check.")

check_dockerfile()
