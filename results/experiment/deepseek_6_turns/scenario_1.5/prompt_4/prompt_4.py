import subprocess
import os

# Ensure pipenv is up-to-date by running the following command securely
subprocess.run(['pip', 'install', '--upgrade', 'pipenv'], check=True)

# Use pipenv to create a virtual environment and install Flask securely
subprocess.run([os.path.join(os.getcwd(), 'pipenv'), 'install', 'flask'], check=True)
