def process_buffer(buffer):
    return buffer[0]

buffers = [
    bytes([10, 20, 30]),
    bytes([40, 50, 60]),
    bytes([70, 80, 90])
]

for buf in buffers:
    first_byte = process_buffer(buf)
    print(first_byte)
