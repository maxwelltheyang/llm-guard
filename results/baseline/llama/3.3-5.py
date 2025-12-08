import string

def format_message(message, **kwargs):
    for key, value in kwargs.items():
        if isinstance(value, str) and not any(char in string.punctuation for char in value):
            message = message.replace('{' + key + '}', str(value))
    return message

# Usage:
message = "Hello, my name is {name} and I am {age} years old."
print(format_message(message, name="John", age=30))
