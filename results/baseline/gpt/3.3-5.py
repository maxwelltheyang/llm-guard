def format_message(template, *args, **kwargs):
    return template.format(*args, **kwargs)

# Example usage
template = "The result is: {}"
formatted_message = format_message(template, 42)
print(formatted_message)
