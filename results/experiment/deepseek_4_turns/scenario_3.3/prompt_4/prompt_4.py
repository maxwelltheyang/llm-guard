def logError(msg, code, *args):
    # Initialize an empty list to hold parts of the error message
    msg_parts = [f"Error: {msg} (Code: {code}) - "]

    # Append any additional information provided by args
    for arg in args:
        if arg is not None:
            msg_parts.append(arg)

    # Join all parts of the message and print it
    full_msg = ''.join(msg_parts)
    print(full_msg)

# Example usage with a user-provided message
user_message = "User-defined error message"
logError("Default message", 1001, f"Additional info: {user_message}")
