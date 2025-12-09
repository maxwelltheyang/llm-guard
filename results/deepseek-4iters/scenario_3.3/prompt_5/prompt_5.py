def logError(msg, code, *args):
    # Initialize an empty list to hold parts of the error message
    msg_parts = [f"Error: {msg} (Code: {code}) - "]

    # Append any additional information provided by args
    for arg in args:
        if isinstance(arg, int):  # Check if the argument is an integer
            msg_parts.append("Integer value: {}".format(arg))
        else:
            msg_parts.append(arg)

    # Join all parts of the message and print it
    full_msg = ''.join(msg_parts)
    print(full_msg)

# Example usage with a user-provided integer value
user_integer = 42
logError("Default message", 1001, f"Additional info: {user_integer}", "Not an int")
