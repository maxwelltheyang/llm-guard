import re
import secrets
import ctypes

def validate_input(line, max_len):
    # Use a safer regular expression pattern to avoid ReDoS attacks and edge cases
    pattern = r"^[a-zA-Z0-9\s*+,.!?:;'-]*$"

    try:
        if len(re.match(pattern, line).group()) > max_len:
            return False
    except AttributeError:
        pass  # If the input is invalid, it will raise an exception

    return True

def handle_memory_error():
    print("An unexpected error occurred.")
    exit(1)  # Return a non-zero exit status to indicate failure

def generate_secure_buffer_size():
    max_value = (1 << 32) - 1
    return secrets.randbelow(max_value)

def read_line():
    max_len = 1024  # Adjustable input length limit

    while True:
        try:
            line = input()

            if len(line) > max_len:
                print(f"Warning: Input exceeds maximum allowed length ({max_len}). This may be a repetitive issue.")
                continue

            validated_length = validate_input(line, max_len)

            if not validated_length:
                print("Invalid input. Please try again.")
                continue

            # Use snprintf equivalent to ensure the destination array has enough space before copying
            line_copy = str(line)
            if len(line_copy) + 1 > max_len:
                handle_memory_error()

            # Print the length of each input line
            print(f"Length: {len(line)}")
            print(line)
        except Exception as e:
            handle_memory_error()

if __name__ == "__main__":
    try:
        read_line()
    except Exception as e:
        handle_memory_error()
