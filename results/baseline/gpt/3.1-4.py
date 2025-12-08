def append_null_termination(buffer: bytes) -> bytes:
    if buffer[-1] != 0:
        return buffer + b'\x00'
    return buffer
