import subprocess
import sys
from os import environ, makedirs
from datetime import datetime

# Ensure logs directory exists
log_dir = 'logs'
makedirs(log_dir, exist_ok=True)

def log_request(method, path):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(f"{log_dir}/requests.log", 'a') as log_file:
        # Log only necessary information and avoid logging sensitive details directly
        log_file.write(f"{timestamp} - {method} request to {path}\n")

def run_command(args):
    try:
        result = subprocess.run([args[0]], check=True, capture_output=True, text=True)
        print(result.stdout)  # Output the standard output of the command
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute command {args[0]}: {e.stderr}", file=sys.stderr)
        exit(1)

# Validate and sanitize inputs before logging or executing commands
def validate_input(input):
    # Basic validation logic to ensure input is safe and appropriate
    if isinstance(input, str):
        # Remove any potentially dangerous characters or limit the length of the input
        validated_input = ''.join(char for char in input if char.isalnum() or char in ['/', '.', '-'])
        return validated_input
    else:
        raise ValueError("Input must be a string")

# Update package lists
run_command(['apt-get', 'update'])

# Install Python 3 and pip
run_command(['apt-get', 'install', '-y', 'python3', 'python3-pip'])

# Log a sample request for demonstration purposes
log_request('GET', validate_input('/initial-setup'))
