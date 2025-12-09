#include <stdio.h>
#include <string.h>
#include <ctype.h> // For isalnum function
#include <stdbool.h> // For bool type

// Function to check if a string contains only alphanumeric characters
bool is_valid_input(const char *str) {
    while (*str) {
        if (!isalnum(*str)) {
            return false;
        }
        str++;
    }
    return true;
}

// Function to read a line of text from standard input and store it in a provided buffer
void read_line(char *buffer, int size) {
    if (fgets(buffer, size, stdin) != NULL) {
        // Remove the newline character if present
        buffer[strcspn(buffer, "\n")] = '\0';

        // Check if the input length exceeds the buffer size
        if (strlen(buffer) >= size - 1) {
            printf("Input too long!\n");
            buffer[0] = '\0'; // Clear the buffer to avoid undefined behavior
        } else if (!is_valid_input(buffer)) {
            printf("Invalid character detected!\n");
            buffer[0] = '\0';
        }
    } else {
        // Handle error: fgets failed or EOF encountered
        perror("Error reading input");
        buffer[0] = '\0'; // Clear the buffer to be safe
    }
}

int main() {
    char buffer[100]; // Example buffer size
    printf("Enter a line of text: ");
    read_line(buffer, sizeof(buffer));
    printf("You entered: %s\n", buffer);
    return 0;
}
