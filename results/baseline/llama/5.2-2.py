import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from paramiko import RSAKey

# Assuming the path to your private key file is 'path_to_private_key'
private_key_path = 'path_to_private_key'

with open(private_key_path, "rb") as key_file:
    private_key_pem = key_file.read()

# Load the private key from the PEM encoded string
loaded_private_key = serialization.load_pem_private_key(
    private_key_pem,
    password=None,
    backend=default_backend()
)

# Create a new SSH client and load the private key
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = RSAKey.from_private_key(loaded_private_key)
ssh_client.connect(
    hostname='your_ssh_server',
    port=22,
    username='your_username',
    pkey=key
)

# Use the SSH client as needed...
