def ensure_termination(buffer):
    buffer += b'\x00'
    return buffer
