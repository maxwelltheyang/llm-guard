import re
import subprocess
import sys

def install_package(package_name):
    # Validate the input to ensure it's safe
    if not re.match(r'^[a-zA-Z0-9_-]+$', package_name):
        raise ValueError("Invalid package name")

    # Use environment variables for sensitive information if necessary
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Example usage
install_package("python-dotenv")
