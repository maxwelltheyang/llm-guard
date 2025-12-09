import os
import time
import tarfile
import subprocess

# Ensure logrotate is enabled and configured correctly
subprocess.run(['systemctl', 'enable', '--now', 'logrotate.service'], check=True)

# Perform log cleanup and compression
logs_to_delete = []
for root, dirs, files in os.walk('/var/logs'):
    for file in files:
        if file.endswith('.log'):
            logfile_path = os.path.join(root, file)
            if os.path.getmtime(logfile_path) < time.time() - 7*3600 and not os.path.islink(logfile_path):
                logs_to_delete.append(logfile_path)

for logfile in logs_to_delete:
    try:
        os.remove(logfile)
        print(f"Deleted old log file: {logfile}")
    except Exception as e:
        print(f"Failed to delete old log file {logfile}: {e}")

try:
    with tarfile.open(f'/var/logs/logs_{time.strftime("%Y%m%d")}.tar.gz', 'w:gz') as tar:
        for root, dirs, files in os.walk('/var/logs'):
            for file in files:
                if file.endswith('.log'):
                    logfile_path = os.path.join(root, file)
                    tar.add(logfile_path, arcname=file)
except Exception as e:
    print(f"Failed to create tar archive: {e}")

# Encryption command whitelist
whitelist = ['/usr/bin/openssl', 'aes-256-cbc']

for root, dirs, files in os.walk('/var/logs'):
    for file in files:
        if file.endswith('.log'):
            logfile_path = os.path.join(root, file)
            encrypted_filename = f'{logfile_path}.enc'
            try:
                subprocess.run(whitelist + ['-in', logfile_path, '-out', encrypted_filename, '-k', os.getenv('ENCRYPTION_KEY', 'default_key')], check=True)
                os.remove(logfile_path)
                print(f"Encrypted and deleted log file: {logfile_path}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to encrypt or delete log file {logfile_path}: {e}")
