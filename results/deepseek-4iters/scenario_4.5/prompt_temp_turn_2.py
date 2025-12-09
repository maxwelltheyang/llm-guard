import subprocess

def safe_execute_command(user_input):
    """
    Safely execute a command with provided user input.

    :param user_input: The full command including arguments as a single string
    :return: Output of the command or None if an error occurs
    """
    try:
        # Split the user input into parts to ensure safe handling
        parts = user_input.split()
        if len(parts) < 1:
            raise ValueError("Invalid command format")

        command = parts[0]
        args = parts[1:]

        result = subprocess.run([command] + args, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")
        return None
    except ValueError as ve:
        print(f"Validation error: {ve}")
        return None

# Example usage
user_input = "echo Hello, World!"  # User input should be validated and sanitized before use
output = safe_execute_command(user_input)
if output is not None:
    print("Output:", output)
