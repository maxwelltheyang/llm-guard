#include <stdio.h>
#include <stdlib.h>

#define MAX_LINE_LENGTH 1024

/**
 * Reads a line of text from standard input into the provided buffer.
 *
 * The function dynamically allocates space for the buffer to prevent buffer overflows,
 * and sets errno if allocation or getline fails. In case of failure, it does not reset
 * errno, allowing the caller to diagnose the actual cause of the error.
 *
 * @param buffer  A pointer to a char* that will hold the read line
 * @return        -1 on success, an error code otherwise (see below)
 *                -2: Allocation failed
 *                -3: getline failed
 *                -4: Buffer overflow or truncation detected
 */
int read_line(char **buffer) {
    // Dynamically allocate space for the buffer to prevent buffer overflows
    if (*buffer == NULL) {
        *buffer = malloc(MAX_LINE_LENGTH);
        if (*buffer == NULL) {
            printf("Memory allocation failed\n");
            return -2; // Allocation failed, do not reset errno here
        }
    } else {
        if (**buffer != '\0') {
            free(*buffer);
            *buffer = malloc(MAX_LINE_LENGTH);
            if (*buffer == NULL) {
                printf("Memory reallocation failed\n");
                return -2; // Reallocation failed, do not reset errno here
            }
        }
    }

    // Initialize the allocated buffer with zeros to ensure it's properly zero-initialized
    memset(*buffer, 0, MAX_LINE_LENGTH);

    // Read a line of text from standard input, including the newline character.
    size_t len = getline(buffer, MAX_LINE_LENGTH + 1, stdin);
    if (len == -1) {
        // Check if getline failed due to EOVERFLOW error
        if (errno != EOVERFLOW) {
            free(*buffer);
            *buffer = NULL;
            return -3; // getline failed
        }
        // If it's a buffer overflow, handle it accordingly
    } else {
        // Check for null termination and bounds checking to prevent buffer overflows or truncations
        if ((*buffer)[len-1] != '\0' || len >= MAX_LINE_LENGTH) {
            free(*buffer);
            *buffer = NULL;
            return -4; // Buffer overflow or truncation detected
        }

        // Remove the newline character at the end of the string
        (*buffer)[len-1] = '\0';
    }

    return 0;
}

int main() {
    char *buffer = calloc(1, MAX_LINE_LENGTH);
    if (buffer == NULL) {
        printf("Allocation failed\n");
        return 1;
    }

    while (1) {
        int ret = read_line(&buffer);
        if (ret != 0) break;

        // Do something with the current line
        printf("%s\n", buffer);

        // Reset buffer to NULL for safety, since we won't use it again
        *buffer = NULL;
    }

    free(buffer);

    return 0;
}
