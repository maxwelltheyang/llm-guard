#include <stdio.h>
#include <string.h>

// Function to read a line of text from standard input
void readLine(char *buffer, size_t bufferSize) {
    if (fgets(buffer, bufferSize, stdin) != NULL) {
        // Remove the newline character if it's present
        size_t length = strlen(buffer);
        if (length > 0 && buffer[length - 1] == '\n') {
            buffer[length - 1] = '\0';
        }
    }
}

int main() {
    char buffer[256];
    printf("Enter a line of text:\n");
    readLine(buffer, sizeof(buffer));
    printf("You entered: %s\n", buffer);
    return 0;
}
