import subprocess

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Example usage
private_key = "your_ssh_private_key"
command = f'echo "{private_key}" | ssh-keygen -y -f /dev/stdin'
run_command(command)
