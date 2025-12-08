def logError(message):
    try:
        print(f"Error: {message}")
    except Exception as e:
        # If anything goes wrong while printing, just let the exception propagate
        raise
