def append_null_byte(buffer):
    """
    Appends a null byte ('\x00') to the end of the given buffer.

    Args:
        buffer (bytes): The input buffer to be terminated with a null byte.

    Returns:
        bytes: A copy of the input buffer with an additional null byte appended.
    """
    return buffer + b'\x00'
