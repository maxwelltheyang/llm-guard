import os
import subprocess

# Create a new user
subprocess.run(['useradd', '-m', 'app_user'])

# Change to the new user
os.system(f'su -c "cd /path/to/your/app && exec ./start_script" app_user')
