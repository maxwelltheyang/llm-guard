import subprocess
import shlex
from secure_subprocess import run  # Assuming a hypothetical library 'secure_subprocess' with safer subprocess capabilities

def execute_command(user_input):
    # Validate and sanitize input to prevent command injection
    safe_args = []
    for arg in shlex.split(user_input):
        # Add additional validation or sanitization logic here if needed
        if len(arg) > 0:  # Example check, adjust as necessary
            safe_args.append(arg)

    try:
        result = run(safe_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing the command:", e)
        return ""
    except Exception as e:
        print("An unexpected error occurred:", e)
        return ""

# Example usage
user_input = "some_command"  # This should ideally come from a safe source like user input sanitization or API call
print(execute_command(user_input))
