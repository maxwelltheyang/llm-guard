def logError(msg, code, *args):
    print(f"Error: {msg} (Code: {code}) - ", end="")

    # Safely handle additional information if provided
    for arg in args:
        if arg is not None:
            print(arg, end="")

    print()

# Simulate user input for the message
user_message = "User-defined error message"

# Call logError with the simulated user input
logError("Default message", 1001, f"Additional info: {user_message}")
