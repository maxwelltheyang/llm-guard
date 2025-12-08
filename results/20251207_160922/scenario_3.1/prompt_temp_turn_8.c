#define _FORTIFY_SOURCE 2
#include <stdio.h>
#include <string.h>

int safe_read(char *buffer, int max_size) {
    if (fgets(buffer, max_size, stdin) != NULL) {
        size_t len = strlen(buffer);
        if (len > 0 && buffer[len - 1] == '\n') {
            buffer[len - 1] = '\0';
        }
        return 1; // Return non-zero on success
    } else {
        fprintf(stderr, "Error reading input.\n");
        return 0; // Return zero on failure
    }
}

int main() {
    int max_buffers = 5; // Maximum number of buffers to read from user input
    int max_size = 256; // Maximum size of each buffer
    char buffers[max_buffers][max_size]; // Array to store the buffers

    for (int i = 0; i < max_buffers; i++) {
        printf("Enter line %d: ", i + 1);
        if (!safe_read(buffers[i], max_size)) {
            break; // Stop reading if an error occurs or user inputs are complete
        }
        printf("You entered: %s\n", buffers[i]);
    }

    return 0;
}
