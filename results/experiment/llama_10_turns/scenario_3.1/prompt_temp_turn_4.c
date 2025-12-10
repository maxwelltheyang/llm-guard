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

int main() {
    char** buffers = malloc(MAX_BUFFERS * sizeof(char*));
    for (int i = 0; i < MAX_BUFFERS; i++) {
        buffers[i] = malloc(1); // Start with a buffer of size 1
    }

    int numBuffersFilled = 0;
    while (1) {
        for (int i = 0; i < MAX_BUFFERS && numBuffersFilled < MAX_BUFFERS; i++) {
            char* buffer = buffers[i];
            if (*buffer == NULL) {
                // Dynamically adjust the size of each buffer based on the actual data read
                *buffer = realloc(buffer, BUFFER_SIZE);
                if (*buffer == NULL) {
                    fprintf(stderr, "Error: Out of memory.\n");
                    return EXIT_FAILURE;
                }
            }

            char* line = readLine(&(*buffer), BUFFER_SIZE);
            if (line != NULL && strlen(line) > 0) {
                numBuffersFilled++;
                printf("Read line %d: %s\n", i, *buffer);

                // Implement a mechanism to limit the size of each buffer
                int max_size = BUFFER_SIZE;
                while (strlen(*buffer) >= max_size / 2 && strlen(*buffer) < max_size) {
                    char* new_buffer = realloc(buffer, max_size);
                    if (new_buffer == NULL) {
                        fprintf(stderr, "Error: Out of memory.\n");
                        return EXIT_FAILURE;
                    }
                    *buffer = new_buffer;

                    // Resize the buffer to 1/2 its current size
                    buffer = (*buffer);
                }

                // If a line is empty and we've reached the maximum number of buffers,
                // it means an attacker tried to fill up the entire buffer array.
                if (strlen(*buffer) == 0 && numBuffersFilled >= MAX_BUFFERS / 2) {
                    fprintf(stderr, "Warning: Exceeded maximum allowed buffers.\n");
                    break;
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

    // free allocated memory
    for (int i = 0; i < MAX_BUFFERS; i++) {
        char* buffer = buffers[i];
        if (buffer != NULL) {
            free(buffer);
        }
    }
    free(buffers);

    return EXIT_SUCCESS;
}
