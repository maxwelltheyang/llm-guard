import os
import pwd
import grp

def run_with_sudo(command):
    # Get current user and group
    username = pwd.getpwuid(os.getuid()).pw_name
    groupname = grp.getgrgid(os.getgid()).gr_name

    # Construct sudo command
    sudo_command = f"sudo -u {username} -g {groupname} {command}"

    # Run the command with sudo
    os.system(sudo_command)

# Example usage:
run_with_sudo("apt-get update")
