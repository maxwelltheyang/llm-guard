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
    int max_size = 256; // Example maximum size of the buffer
    char buffer[max_size]; // Use a fixed-size array for input

    printf("Enter a line of text: ");
    if (safe_read(buffer, max_size)) {
        printf("You entered: %s\n", buffer);
    }

    return 0;
}
