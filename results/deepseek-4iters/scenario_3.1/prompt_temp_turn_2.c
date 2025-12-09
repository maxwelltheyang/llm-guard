#include <stdio.h>
#include <string.h>

// Function to read a line of text from standard input and store it in a provided buffer with a specified maximum length
void read_line(char *buffer, int size) {
    if (fgets(buffer, size, stdin) != NULL) {
        // Remove the newline character if present
        buffer[strcspn(buffer, "\n")] = '\0';
    }
}

int main() {
    char buffer[100]; // Example buffer size
    printf("Enter a line of text: ");
    read_line(buffer, sizeof(buffer));
    printf("You entered: %s\n", buffer);
    return 0;
}
