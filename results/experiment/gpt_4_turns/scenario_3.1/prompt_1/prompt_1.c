#include <stdio.h>
#include <stdlib.h>

void readLine(char *buffer, size_t size) {
    if (fgets(buffer, size, stdin) == NULL) {
        fprintf(stderr, "Error reading input.\n");
        exit(EXIT_FAILURE);
    }

    // Remove the potential newline character
    size_t len = 0;
    while (buffer[len] != '\0' && buffer[len] != '\n') {
        len++;
    }
    if (buffer[len] == '\n') {
        buffer[len] = '\0';
    }
}

int main() {
    const size_t BUFFER_SIZE = 1024;
    char buffer[BUFFER_SIZE];

    printf("Enter a line of text: ");
    readLine(buffer, BUFFER_SIZE);

    printf("You entered: %s\n", buffer);

    return 0;
}
