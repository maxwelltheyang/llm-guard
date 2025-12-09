#include <stdio.h>
#include <string.h>

void readLine(char *buffer, int bufferSize) {
    if (fgets(buffer, bufferSize, stdin) != NULL) {
        // Remove newline character if present
        char *newline = strchr(buffer, '\n');
        if (newline != NULL) {
            *newline = '\0';
        }
    } else {
        // Clear the buffer if input reading fails
        if (bufferSize > 0) {
            buffer[0] = '\0';
        }
    }
}

int main() {
    char buffer[256];
    printf("Enter a line of text: ");
    readLine(buffer, sizeof(buffer));
    printf("You entered: %s\n", buffer);
    return 0;
}
