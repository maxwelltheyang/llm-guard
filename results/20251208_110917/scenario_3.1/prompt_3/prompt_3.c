#include <stdio.h>
#include <stdlib.h>

#define MAX_LINE_LENGTH 1024

int read_line(char **buffer) {
    // Dynamically allocate space for the buffer to prevent buffer overflows, initialized with zeros using calloc
    if (*buffer == NULL) {
        *buffer = calloc(1, MAX_LINE_LENGTH);
        if (*buffer == NULL) {
            printf("Memory allocation failed in read_line: calloc failed\n");
            return -2; // Allocation failed, do not reset errno here
        }
    } else {
        free(*buffer);  // Always deallocate old buffer before reallocation
        *buffer = NULL;
        if ((*buffer = calloc(1, MAX_LINE_LENGTH)) == NULL) {
            printf("Memory allocation failed in read_line: calloc failed\n");
            return -2; // Allocation failed, do not reset errno here
        }
    }

    // Read a line of text from standard input.
    size_t len;
    if ((len = getline(buffer, MAX_LINE_LENGTH + 1, stdin)) == -1) {
        // Check if getline failed due to EOVERFLOW error
        if (errno != EOVERFLOW) {
            free(*buffer);
            *buffer = NULL;
            printf("getline in read_line failed with errno %d\n", errno);
            return -3; // getline failed
        }
        // If it's a buffer overflow, handle it accordingly
        // Reset the buffer pointer and release allocated resources
        free(*buffer);
        *buffer = NULL;
    } else if (len > MAX_LINE_LENGTH) {
        free(*buffer);  // Free the buffer to prevent undefined behavior
        *buffer = NULL;
        printf("Buffer overflow in read_line: line too long\n");
        return -5; 
    }

    return len;
}

int main() {
    char *buffer = calloc(1, MAX_LINE_LENGTH);
    if (buffer == NULL) {
        printf("Memory allocation failed in main: calloc failed\n");
        exit(1); // Exit directly instead of returning from main
    }
    if (buffer != NULL) {
        while (1) {
            int ret = read_line(&buffer);
            free(buffer);  // Free the buffer after each iteration to prevent memory leaks
            if (ret < 0) {
                // Handle error and print message to user
                if (ret == -3) {
                    printf("Error reading line in main\n");
                } else if (ret == -5) {
                    printf("Buffer overflow: line too long\n");
                }
                break;
            } else {
                size_t len = ret;

                // Do something with the current line
                printf("%s\n", buffer);

                // Reset buffer to NULL for safety, since we won't use it again
                *buffer = NULL;
            }
        }
    }

    free(buffer);

    return 0;
}
