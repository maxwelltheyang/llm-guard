import subprocess
import sys

# Update package lists
process = subprocess.run(['apt-get', 'update'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
if process.returncode != 0:
    print("Failed to update package lists.", file=sys.stderr)
    exit(1)

# Install Python 3 and pip
process = subprocess.run(['apt-get', 'install', '-y', 'python3', 'python3-pip'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
if process.returncode != 0:
    print("Failed to install Python 3 and pip.", file=sys.stderr)
    exit(1)
