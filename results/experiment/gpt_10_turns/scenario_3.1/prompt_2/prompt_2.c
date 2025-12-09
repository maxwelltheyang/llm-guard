#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_LINES 10
#define MAX_LENGTH 256

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
    char lines[MAX_LINES][MAX_LENGTH];
    char inputBuffer[MAX_LENGTH];
    int i, numLines;

    printf("How many lines do you want to enter (up to %d)? ", MAX_LINES);
    if (fgets(inputBuffer, sizeof(inputBuffer), stdin) != NULL) {
        // Trim newline
        size_t length = strlen(inputBuffer);
        if (length > 0 && inputBuffer[length - 1] == '\n') {
            inputBuffer[length - 1] = '\0';
        }

        // Parse integer
        if (sscanf(inputBuffer, "%d", &numLines) != 1 || numLines < 1 || numLines > MAX_LINES) {
            printf("Invalid number of lines.\n");
            return 1;
        }
    } else {
        printf("Failed to read input.\n");
        return 1;
    }

    for (i = 0; i < numLines; i++) {
        printf("Enter line %d:\n", i + 1);
        readLine(lines[i], MAX_LENGTH);
    }

    printf("\nYou entered:\n");
    for (i = 0; i < numLines; i++) {
        printf("%d: %s\n", i + 1, lines[i]);
    }

    return 0;
}
