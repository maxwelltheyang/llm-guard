def process_string(s):
    # This is a placeholder for your processing logic
    return s[:10]  # Just taking the first 10 characters as an example

# Test with a very long input string
long_string = "a" * 1000000  # Creating a very long string
result = process_string(long_string)
print(result)  # Should print the first 10 characters of the long string
