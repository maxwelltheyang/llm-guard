import math

def calculate_checksum(buffer):
    return sum(buffer) % 256

for i in range(10):  # example: 10 buffers to process
    buffer = [i for i in range(1024)]  # example: 1KB buffer filled with numbers from 0 to 1023
    checksum = calculate_checksum(buffer)
    print(f"Buffer {i}: first byte is {buffer[0]} and checksum is {checksum}")
