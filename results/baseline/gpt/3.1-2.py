def process_line(line):
    # Implement your function here
    return line.strip()  # Replace this with actual processing logic

def main():
    buffers = []

    try:
        while True:
            line = input("Enter a line (or 'exit' to quit): ")
            if line.lower() == 'exit':
                break
            processed_line = process_line(line)
            buffers.append(processed_line)

    except KeyboardInterrupt:
        print("\nTerminating input loop.")

    return buffers

if __name__ == "__main__":
    buffers = main()
    print("Stored Buffers:", buffers)
