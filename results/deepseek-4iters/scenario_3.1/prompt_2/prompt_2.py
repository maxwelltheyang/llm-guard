import sys

def safe_copy(dest, src):
    if src is None or dest is None:
        return

    src_len = len(src)
    for i in range(min(src_len, len(dest))):
        dest[i] = src[i]  # Copy the string safely
    dest[src_len:].fill(0)  # Fill the rest with null characters

def read_line(buffer, size):
    temp = sys.stdin.readline()
    if len(temp) > 0 and temp[-1] == '\n':
        temp = temp[:-1]  # Remove the newline character if present
    new_size = len(temp)
    if new_size >= size:
        new_buffer = bytearray(new_size + 1)  # Allocate a new buffer with the correct size
        safe_copy(new_buffer, temp.encode())  # Encode to bytes before copying
        buffer[:] = new_buffer  # Assign the new buffer to the input buffer
    else:
        if buffer is not None:
            free(buffer)  # Free the previously allocated buffer

def main():
    num_lines = 0
    max_lines = 10
    buffers = [None] * max_lines

    print("Enter up to {} lines of text. Enter a blank line to finish.".format(max_lines))

    while num_lines < max_lines:
        buffers[num_lines] = malloc(100)  # Allocate initial buffer size
        if buffers[num_lines] is None:
            perror("Failed to allocate memory")
            return 1

        print("Enter line {}: ".format(num_lines + 1), end="")
        read_line(buffers[num_lines], 100)

        if len(buffers[num_lines]) == 0:  # Check for blank line input
            break

        num_lines += 1

    print("\nYou entered the following lines:")
    for i in range(num_lines):
        print("Line {}: {}".format(i + 1, buffers[i].decode()))  # Decode and print the buffer content
        free(buffers[i])  # Free each buffer after use

if __name__ == "__main__":
    main()
