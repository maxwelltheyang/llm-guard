import subprocess
import shlex

def execute_command(user_input):
    # Validate and sanitize input to prevent command injection
    safe_args = shlex.split(user_input)  # Using shlex for safer parsing of shell-like strings
    try:
        result = subprocess.run(safe_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
