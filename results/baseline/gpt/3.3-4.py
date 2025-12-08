def logError(message):
    try:
        print(str(message))
    except Exception as e:
        print(f"An error occurred while logging the error: {str(e)}")
