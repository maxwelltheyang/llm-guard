#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
#include <unistd.h>

#define PASS_LENGTH 16
#define UPPERCASE 'A'
#define LOWERCASE 'a'

char* generate_password() {
    char* password = malloc(PASS_LENGTH + 1);

    if (password == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }

    FILE* urandom;
    int attempts = 0;

    do {
        urandom = fopen("/dev/urandom", "rb");

        if (!urandom && attempts < 5) {
            printf("Failed to open /dev/urandom. Retrying in 1 second...\n");
            sleep(1);
            attempts++;
        } else if (!urandom) {
            fprintf(stderr, "Failed to open /dev/urandom after %d retries\n", attempts + 1);
            free(password);
            exit(1);
        }
    } while (!urandom);

    char* random_bytes = malloc(PASS_LENGTH);

    if (random_bytes == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(urandom);
        free(password);
        exit(1);
    }

    // Read from /dev/urandom into the buffer
    int bytes_read = fread(random_bytes, 1, PASS_LENGTH, urandom);

    if (ferror(urandom)) {
        fprintf(stderr, "Error reading from /dev/urandom: %s\n", strerror(errno));
        fclose(urandom);
        free(password);
        free(random_bytes);
        exit(1);
    }

    // Check for short read
    if (bytes_read != PASS_LENGTH) {
        fprintf(stderr, "Short read from /dev/urandom. This should not happen.\n");
        fclose(urandom);
        free(password);
        free(random_bytes);
        exit(1);
    }

    // Convert the bytes to a string and copy into password array
    for (int i = 0; i < PASS_LENGTH; ++i) {
        password[i] = LOWERCASE <= random_bytes[i] && random_bytes[i] <= 'z' ? random_bytes[i] + ('A' - 'a') : random_bytes[i];
    }

    // Add a null terminator
    password[PASS_LENGTH] = '\0';

    fclose(urandom);
    free(random_bytes);

    return password;
}

int main() {
    char* pass = generate_password();
    printf("Random Password: %s\n", pass);

    free(pass);

    return 0;
}
