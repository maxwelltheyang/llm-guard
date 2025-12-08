import threading
from queue import Queue

def read_line(line_num, lock):
    with open('input.txt', 'r') as f:
        return f.readline().strip()

def process_buffer(buffer):
    # Process the buffer here (e.g., print it)
    pass

def main():
    line_num = 0
    buffers = []
    queue = Queue()
    lock = threading.Lock()

    while True:
        with lock:
            if len(buffers) < 10 and line_num < 10000: # Read at most 10 buffers or 10000 lines
                buffer = read_line(line_num, lock)
                if buffer != '':
                    buffers.append(buffer)
                    line_num += 1
                else:
                    break

        for i in range(len(buffers) - 1):
            thread = threading.Thread(target=process_buffer, args=(buffers[i],))
            thread.daemon = True # So the thread dies when main thread exits
            thread.start()

        if len(buffers) > 0:
            process_buffer(buffers[-1]) # Process the last buffer

if __name__ == "__main__":
    main()
