import subprocess
import sys
from os import environ

def run_command(args):
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        print(result.stdout)  # Output the standard output of the command
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute command {' '.join(args)}: {e.stderr}", file=sys.stderr)
        exit(1)

# Update package lists
run_command(['apt-get', 'update'])

# Install Python 3 and pip
run_command(['apt-get', 'install', '-y', 'python3', 'python3-pip'])
