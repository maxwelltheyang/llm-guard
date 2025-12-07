def format_message(template, *args, **kwargs):
    return template.format(*args, **kwargs)

message_template = "The value is: {}"
formatted_message = format_message(message_template, 42)
print(formatted_message)
