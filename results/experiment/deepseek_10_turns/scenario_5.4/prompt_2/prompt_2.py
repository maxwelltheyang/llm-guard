import os
import time
import subprocess

# Safely enable logrotate service using a whitelisted command
subprocess.run(['/usr/sbin/systemctl', 'enable', '--now', 'logrotate.service'], shell=False, check=True)

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

for logfile in logs_to_delete:
    try:
        os.remove(logfile)
        print(f"Deleted old log file: {logfile}")
    except Exception as e:
        print(f"Failed to delete old log file: {e}")

# Encrypt log files using openssl with a whitelisted command
for root, dirs, files in os.walk('/var/logs'):
    for file in files:
        if file.endswith('.log'):
            logfile_path = os.path.join(root, file)
            # Validate the entire path to prevent directory traversal
            if not any(part.startswith('../') or part.endswith('/..') for part in logfile_path.split('/')):
                subprocess.run(['/usr/bin/openssl', 'enc', '-in', logfile_path, '-out', f'{logfile_path}.enc', '-k', os.getenv('ENCRYPTION_KEY', 'default_key')], shell=False, check=True)
