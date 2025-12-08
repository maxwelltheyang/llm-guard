import logging

def log_error(*args):
    # Assuming you want to format the message using str.format or f-string
    msg = ' '.join(map(str, args))
    logging.error(msg)
