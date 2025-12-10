#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * Reads a line of text from standard input and stores it in the provided buffer.
 *
 * @param buffer The buffer to store the line of text.
 * @param size  The initial capacity of the buffer. If NULL, will be dynamically resized using realloc().
 */
void* readLine(char** buffer, int size) {
    if (fgets(*buffer, size + 1, stdin) == NULL) {
        fprintf(stderr, "Error reading from standard input: %s\n", strerror(errno));
        return NULL;
    }

    // Remove the trailing newline character
    (*buffer)[strcspn((*buffer), "\n")] = 0;

    // Check for empty lines or null inputs
    if (strlen(*buffer) == 0 || (*buffer)[0] == '\0') {
        fprintf(stderr, "Error: Empty line read from standard input.\n");
        return NULL;
    }

    return *buffer;
}

#define MAX_BUFFERS 1024

// Custom error handling function to handle memory allocation failures
static void handle_memory_error(const char* message) {
    fprintf(stderr, "Error: %s\n", message);
    exit(EXIT_FAILURE); // Return a non-zero exit status to indicate failure
}

int main() {
    char** buffers = malloc(MAX_BUFFERS * sizeof(char*));
    if (buffers == NULL) {
        handle_memory_error("Failed to allocate memory for buffer array");
    }

    for (int i = 0; i < MAX_BUFFERS; i++) {
        buffers[i] = malloc(1); // Start with a buffer of size 1
        if (buffers[i] == NULL) {
            handle_memory_error("Failed to allocate memory for buffer");
        }
    }

    int numBuffersFilled = 0;
    while (1) {
        for (int i = 0; i < MAX_BUFFERS && numBuffersFilled < MAX_BUFFERS; i++) {
            char* buffer = buffers[i];
            if (*buffer == NULL) {
                // Dynamically adjust the size of each buffer based on the actual data read
                *buffer = realloc(buffer, BUFFER_SIZE);
                if (*buffer == NULL) {
                    handle_memory_error("Failed to allocate memory for buffer");
                }
            }

            char* line = readLine(&(*buffer), BUFFER_SIZE);
            if (line != NULL && strlen(line) > 0) {
                numBuffersFilled++;
                printf("Read line %d: %s\n", i, *buffer);

                // Implement input validation to check for excessively large or malicious inputs
                if (strlen(*buffer) >= BUFFER_SIZE / 2 || strlen(*buffer) > MAX_BUFFER_SIZE) {
                    fprintf(stderr, "Warning: Input string too long. Truncating.\n");
                    (*buffer)[BUFFER_SIZE - 1] = '\0';
                }

                // If a line is empty and we've reached the maximum number of buffers,
                // it means an attacker tried to fill up the entire buffer array.
                if (strlen(*buffer) == 0 && numBuffersFilled >= MAX_BUFFERS / 2) {
                    fprintf(stderr, "Warning: Exceeded maximum allowed buffers.\n");
                    break;
                }

                // Dynamically resize the buffer based on actual data read
                while (strlen(*buffer) > BUFFER_SIZE / 2) {
                    char* new_buffer = realloc(buffer, BUFFER_SIZE);
                    if (new_buffer == NULL) {
                        handle_memory_error("Failed to allocate memory for buffer");
                    }
                    *buffer = new_buffer;

                    // Resize the buffer to 1/2 its current size
                    buffer = (*buffer);

                    if (strlen(*buffer) <= BUFFER_SIZE / 2) {
                        break;
                    }

                    BUFFER_SIZE *= 2; // Increase buffer size by a factor of 2
                }
            } else if (*buffer != NULL) {
                free(*buffer);
                *buffer = NULL;
            }
        }

        // Check for end of file
        if (numBuffersFilled < MAX_BUFFERS && feof(stdin)) {
            break; // End of file reached
        }
    }

    // Free allocated memory
    for (int i = 0; i < MAX_BUFFERS; i++) {
        char* buffer = buffers[i];
        if (buffer != NULL) {
            free(buffer);
        }
    }
    free(buffers);

    return EXIT_SUCCESS;
}
