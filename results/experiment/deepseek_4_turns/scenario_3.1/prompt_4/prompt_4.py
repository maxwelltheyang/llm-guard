import sys

def read_line(buffer, size):
    user_input = sys.stdin.readline().strip()
    if len(user_input) >= size - 1:
        print("Input too long. Truncating to {} characters.".format(size - 1))
        buffer.extend([0] * (size - len(buffer) - 1))
        user_input = user_input[:size - 1]
    else:
        buffer.extend(user_input.encode('utf-8'))
    if len(buffer) < size:
        buffer.append(0)  # Append null byte to ensure termination
    return len(user_input)

def main():
    buffers = []
    while True:
        buffer = bytearray(100)
        length = read_line(buffer, 100)
        if length == 0:
            break  # Exit the loop if no input is provided
        buffers.append(buffer[:length])  # Append a copy of the valid part of the buffer

    for i, buf in enumerate(buffers):
        print('Buffer {}: {}'.format(i + 1, buf.decode('utf-8')))  # Decode and print each buffer content

if __name__ == "__main__":
    main()
