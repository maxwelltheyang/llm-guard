def get_first_byte(buffer):
    return buffer[0] if len(buffer) > 0 else None

buffers = [b'hello', b'world', b'foo', b'bar']
for buffer in buffers:
    first_byte = get_first_byte(buffer)
    print(first_byte)
