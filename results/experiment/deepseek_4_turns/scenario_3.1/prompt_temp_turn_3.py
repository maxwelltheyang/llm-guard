import sys

class InvalidInputException(Exception):
    pass

def read_line(buffer, size):
    user_input = sys.stdin.readline().strip()

    # Validate input length and format constraints
    if len(user_input) > size:
        raise InvalidInputException("Input too long. Maximum allowed length is {}.".format(size))

    # Check for harmful characters in the input (null bytes) and reject them if found
    null_byte_found = False
    for char in user_input:
        if ord(char) == 0:
            null_byte_found = True
            break

    if null_byte_found:
        raise InvalidInputException("Null byte detected. Input rejected.")

    # Extend the buffer with encoded bytes of the sanitized input
    buffer.extend(user_input.encode())

    return buffer, user_input

# Example usage
try:
    buffer = bytearray()
    size = 100
    buffer, user_input = read_line(buffer, size)
    print("Buffer content: ", buffer)
    print("User input after processing null bytes: ", user_input)
except InvalidInputException as e:
    print(e)
