import os
import sys
import subprocess

if not os.geteuid() == 0:
    print("This script requires root privileges. Please run with sudo.")
    sys.exit(1)

# Your main script logic here
print("Script is running with root privileges.")

# Example: using a command that requires root
# subprocess.run(['apt-get', 'update'])

