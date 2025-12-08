import os

# Define a list of necessary ports
ports = [80, 443]  # HTTP and HTTPS

# Iterate over each port
for port in ports:
    # Create the rule to allow incoming traffic on this port
    command = f"sudo ufw allow {port}/tcp"

    # Execute the command
    os.system(command)
