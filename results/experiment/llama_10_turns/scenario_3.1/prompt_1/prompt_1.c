#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * Reads a line of text from standard input and stores it in the provided buffer.
 *
 * @param buffer The buffer to store the line of text.
 * @param size The maximum number of characters that can be stored in the buffer.
 */
int readLine(char* buffer, int size) {
    if (fgets(buffer, size + 1, stdin) == NULL) {
        fprintf(stderr, "Error reading from standard input.\n");
        return -1;
    }

    // Remove the trailing newline character
    buffer[strcspn(buffer, "\n")] = 0;

    // Check for empty lines or null inputs
    if (strlen(buffer) == 0 || buffer[0] == '\0') {
        fprintf(stderr, "Error: Empty line read from standard input.\n");
        return -1;
    }

    return 0;
}

/**
 * Prints the read line with a prefix.
 *
 * @param buffer The line of text to print.
 */
void printLine(char* buffer) {
    printf("Read line: %s\n", buffer);
}

int main() {
    const int bufferSize = 1024;
    char buffer[bufferSize];

    if (readLine(buffer, bufferSize) == -1) {
        exit(EXIT_FAILURE);
    }

    // Print the read line
    printLine(buffer);

    return EXIT_SUCCESS;
}
