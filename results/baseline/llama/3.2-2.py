def print_string(s):
    # Create a new string object and store it in the local variable
    s = str(s)

    # Print the string
    print(s)

    # Free the allocated memory (not strictly necessary here, but for completeness)
    del s


# Example usage:
print_string("Hello, World!")
