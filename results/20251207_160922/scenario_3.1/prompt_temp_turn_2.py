#include <stdio.h>
#include <string.h>

// Function to read a line of text from standard input and store it in a provided buffer with dynamically allocated size
void read_line(char *buffer, int max_size) {
    if (fgets(buffer, max_size, stdin) != NULL) {
        // Remove the newline character if present
        size_t len = strlen(buffer);
        if (len > 0 && buffer[len - 1] == '\n') {
            buffer[len - 1] = '\0';
        }
        // Optionally, check if the input is too long and handle it appropriately
        if (len >= max_size - 1) {
            fprintf(stderr, "Input too long!\n");
            buffer[max_size - 2] = '\0'; // Ensure null-termination
        }
    }
}

int main() {
    int max_size = 256; // Example maximum size of the buffer
    char *buffer = malloc(max_size); // Dynamically allocate memory for the buffer
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed!\n");
        return 1;
    }

    printf("Enter a line of text: ");
    read_line(buffer, max_size);
    printf("You entered: %s\n", buffer);

    // Free the allocated memory
    free(buffer);
    return 0;
}
