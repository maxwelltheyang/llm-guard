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

#define MAX_BUFFERS 1024
#define BUFFER_SIZE 1024

int main() {
    char** buffers = malloc(MAX_BUFFERS * sizeof(char*));
    for (int i = 0; i < MAX_BUFFERS; i++) {
        buffers[i] = malloc(BUFFER_SIZE * sizeof(char));
    }

    int numBuffersFilled = 0;
    while (1) {
        int result;
        for (int i = 0; i < MAX_BUFFERS && numBuffersFilled < MAX_BUFFERS; i++) {
            if ((result = readLine(buffers[i], BUFFER_SIZE)) == -1) {
                fprintf(stderr, "Error reading line from standard input.\n");
                return EXIT_FAILURE;
            }
            if (buffers[i][0] == '\0') break; // empty line or end of file
            numBuffersFilled++;
        }

        if (numBuffersFilled < MAX_BUFFERS && feof(stdin)) {
            break; // end of file reached
        }

        for (int i = 0; i < numBuffersFilled; i++) {
            printf("Read line %d: %s\n", i, buffers[i]);
        }
    }

    // free allocated memory
    for (int i = 0; i < MAX_BUFFERS; i++) {
        free(buffers[i]);
    }
    free(buffers);

    return EXIT_SUCCESS;
}
