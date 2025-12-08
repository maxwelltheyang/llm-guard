def test_long_input_string(func):
    # Create a very long input string by repeating a pattern
    long_input = "abc" * (10**6)  # Adjust the multiplier to change the length
    result = func(long_input)
    return result

# Example of using the function with a sample function to test
def sample_function(s):
    return len(s)

# Run the test
print(test_long_input_string(sample_function))
