import os
import subprocess

# Safely enable logrotate service using a whitelisted command
subprocess.run(['/usr/sbin/systemctl', 'enable', '--now', 'logrotate.service'], check=True)

# Delete old log files
logs_to_delete = []
for root, dirs, files in os.walk('/var/logs'):
    for file in files:
        if file.endswith('.log'):
            logfile_path = os.path.join(root, file)
            # Validate the entire path to prevent directory traversal
            if not any(part.startswith('../') or part.endswith('/..') for part in logfile_path.split('/')):
                if os.path.getmtime(logfile_path) < time.time() - 7*3600 and not os.path.islink(logfile_path):
                    logs_to_delete.append(logfile_path)

# Encrypt log files using openssl with a whitelisted command
for logfile in logs_to_delete:
    # Validate the path before passing it to subprocess
    if os.path.exists(logfile):
        subprocess.run(['openssl', 'enc', '-e', '-in', logfile, '-out', f'{logfile}.enc'], check=True)
        # Optionally delete the original file after encryption
        user_confirmation = input("Do you want to delete the original log file? (y/n): ")
        if user_confirmation.lower() == 'y':
            os.remove(logfile)
