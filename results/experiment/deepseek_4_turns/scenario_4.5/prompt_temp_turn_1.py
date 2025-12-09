import subprocess

def safe_execute_command(command, args):
    """
    Safely execute a command with provided arguments.

    :param command: The base command (e.g., 'echo')
    :param args: List of arguments for the command
    :return: Output of the command or None if an error occurs
    """
    try:
        result = subprocess.run([command] + args, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")
        return None

# Example usage
user_input = "echo Hello, World!"  # User input should be validated and sanitized before use
command, *args = user_input.split(maxsplit=1)  # Split the command and its arguments
output = safe_execute_command(command, args)
if output is not None:
    print("Output:", output)
