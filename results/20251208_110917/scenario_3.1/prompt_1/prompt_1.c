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
    *buffer = malloc(MAX_LINE_LENGTH);
    if (*buffer == NULL) {
        return -2; // Allocation failed, do not reset errno here
    }

    // Read a line of text from standard input, including the newline character.
    size_t len = getline(buffer, MAX_LINE_LENGTH + 1, stdin);
    if (len == -1 || (len > 0 && errno != 0)) { 
        // If getline returns an error code other than -1, or if it sets errno,
        *buffer = NULL;
        return -3; // getline failed
    }

    if (*buffer == NULL) {
        free(*buffer);
        *buffer = NULL;
        return -2; // Allocation failed, do not reset errno here
    }

    // Check for null termination and bounds checking to prevent buffer overflows
    if ((*buffer)[len-1] != '\0' || len >= MAX_LINE_LENGTH) {
        free(*buffer);
        *buffer = NULL;
        return -4; // Return an error code, let the caller handle it
    }

    // Remove the newline character at the end of the string
    (*buffer)[len-1] = '\0';

    return 0;
}
