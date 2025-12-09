#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

// Function to check if a string contains only alphanumeric characters
bool is_valid_input(const char *str, size_t length) {
    for (size_t i = 0; i < length; ++i) {
        if (!isalnum(str[i])) {
            return false;
        }
    }
    return true;
}

// Function to read a line of text from standard input and store it in a buffer
void read_line(char *buffer, int size) {
    if (fgets(buffer, size, stdin) == NULL) {
        fprintf(stderr, "Error: Could not read input.\n");
        return;
    }

    // Remove the newline character if present at the end of the buffer
    size_t length = strlen(buffer);
    if (length > 0 && buffer[length - 1] == '\n') {
        buffer[length - 1] = '\0';
        --length;
    }

    // Check if the input contains invalid characters
    if (!is_valid_input(buffer, length)) {
        fprintf(stderr, "Invalid character detected! The input must contain only alphanumeric characters.\n");
        buffer[0] = '\0'; // Clear the buffer to avoid undefined behavior
    }
}

int main() {
    char buffer[100]; // Example buffer size
    printf("Enter a line of text: ");
    read_line(buffer, sizeof(buffer));
    printf("You entered: %s\n", buffer);
    return 0;
}
