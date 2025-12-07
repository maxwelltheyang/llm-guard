def safe_function():
    try:
        # risky operation
        dangerous_operation()
    except Exception as e:
        print(f"An error occurred: {e}")
