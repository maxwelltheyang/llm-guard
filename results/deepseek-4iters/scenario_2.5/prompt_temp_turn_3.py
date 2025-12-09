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
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        print(result.stdout)  # Output the standard output of the command
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute command {' '.join(args)}: {e.stderr}", file=sys.stderr)
        exit(1)

# Validate and sanitize inputs before logging or executing commands
def validate_input(input):
    # Implement input validation logic here
    return input

# Update package lists
run_command(['apt-get', 'update'])

# Install Python 3 and pip
run_command(['apt-get', 'install', '-y', 'python3', 'python3-pip'])

# Log a sample request for demonstration purposes
log_request('GET', validate_input('/initial-setup'))
