import os
import time
from subprocess import run, DEVNULL

# Safely enable logrotate service using a whitelisted command
try:
    result = run(['/usr/sbin/systemctl', 'enable', '--now', 'logrotate.service'], check=True, stdout=DEVNULL, stderr=DEVNULL)
except subprocess.CalledProcessError as e:
    print(f"Failed to enable logrotate service: {e}")
    exit(1)

# Define the directory and file extension to target
target_directory = '/var/logs'
file_extension = '.log'

# Collect .log files within the specified directory, ensuring only valid paths are used
logs_to_delete = []
try:
    ls_output = run(['ls', '-d', target_directory], check=True, capture_output=True, text=True)
    for line in ls_output.stdout.splitlines():
        root = line.strip()
        if os.path.isdir(root):
            for file in os.listdir(root):
                if file.endswith(file_extension) and not any(part.startswith('../') or part.endswith('/..') for part in os.path.join(root, file).split('/')):
                    logfile_path = os.path.join(root, file)
                    # Check if the file is older than 7 hours
                    if os.path.getmtime(logfile_path) < time.time() - 7*3600 and not os.path.islink(logfile_path):
                        logs_to_delete.append(logfile_path)
except subprocess.CalledProcessError as e:
    print(f"Failed to list directory contents: {e}")
    exit(1)

# Encrypt log files using openssl with a whitelisted command, ensuring only valid paths are used
for logfile in logs_to_delete:
    if os.path.exists(logfile):
        try:
            result = run(['openssl', 'enc', '-e', '-in', logfile, '-out', f'{logfile}.enc'], check=True, stdout=DEVNULL, stderr=DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Failed to encrypt {logfile}: {e}")
            continue

        # Optionally delete the original file after encryption
        user_confirmation = input("Do you want to delete the original log file? (y/n): ")
        if user_confirmation.lower() == 'y':
            try:
                os.remove(logfile)
            except OSError as e:
                print(f"Failed to delete {logfile}: {e}")
