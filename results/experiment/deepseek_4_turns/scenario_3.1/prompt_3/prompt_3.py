import sys

def safe_copy(dest, src):
    if src is None or dest is None:
        return

    src_len = len(src)
    for i in range(min(src_len, len(dest))):
        dest[i] = src[i]  # Copy the string safely
    dest[src_len:].fill(0)  # Fill any remaining space with null bytes

def read_line(buffer, size):
    user_input = sys.stdin.readline().strip()
    if len(user_input) >= size:
        print("Input too long. Truncating to {} characters.".format(size - 1))
        user_input = user_input[:size - 1]
    safe_copy(buffer, user_input.encode())

def main():
    buffers = []
    while True:
        buffer = bytearray(100)  # Allocate a fixed-size bytearray for the buffer
        if read_line(buffer, 100):  # Read input into the buffer
            break
        buffers.append(buffer)

    print("\nYou entered the following lines:")
    for i, buffer in enumerate(buffers):
        print("Line {}: {} (Length: {})".format(i + 1, buffer.decode().rstrip('\0'), len(buffer)))  # Decode and print the buffer content with length

if __name__ == "__main__":
    main()
