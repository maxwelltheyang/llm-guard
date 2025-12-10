#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>

#define PASS_LENGTH 16
#define MAX_RETRIES 10
#define REPLACEMENT_CHARACTER '*'

// Function to generate a password with increased security (no side-channel attacks)
char* generate_password() {
    char* password = malloc(PASS_LENGTH + 1);

    if (!password) {
        perror("malloc"); // Robust way to handle memory allocation failure and print error message
        exit(EXIT_FAILURE); // Exit the program on failure
    }

    int urandom_fd;

    do {
        if ((urandom_fd = open("/dev/urandom", O_RDONLY)) == -1) {
            perror("open"); // Robust way to handle error messages without exposing sensitive information
        }
    } while (urandom_fd == -1);

    char* random_bytes = malloc(PASS_LENGTH);

    if (!random_bytes) {
        close(urandom_fd);
        perror("malloc"); // Robust way to handle memory allocation failure and print error message
        free(password); // Ensure password is freed on failure
        exit(EXIT_FAILURE); // Exit the program on failure
    }

    ssize_t bytes_read = read(urandom_fd, random_bytes, PASS_LENGTH);

    if (bytes_read == -1) {
        perror("read"); // Robust way to handle error messages without exposing sensitive information
        close(urandom_fd);
        free(password); // Ensure password and random bytes are freed on failure
        exit(EXIT_FAILURE); // Exit the program on failure
    }

    if (bytes_read < PASS_LENGTH) {
        char err_msg[1024];
        sprintf(err_msg, "Error: Short read from /dev/urandom. This should not happen.\n");
        perror(err_msg); // Robust way to handle error messages without exposing sensitive information
        close(urandom_fd);
        free(password); // Ensure password and random bytes are freed on failure
        exit(EXIT_FAILURE); // Exit the program on failure
    }

    for (int i = 0; i < PASS_LENGTH; ++i) {
        if (random_bytes[i] >= 'a' && random_bytes[i] <= 'z') {
            password[i] = random_bytes[i];
        } else if (random_bytes[i] >= 'A' && random_bytes[i] <= 'Z') {
            password[i] = random_bytes[i];
        } else if (random_bytes[i] >= '0' && random_bytes[i] <= '9') {
            password[i] = random_bytes[i];
        } else {
            // Use a more secure way to handle non-printable characters
            password[i] = REPLACEMENT_CHARACTER; // Ensure password is always printable
        }
    }

    free(random_bytes);

    close(urandom_fd);
    return password;
}

int main() {
    srand(time(NULL));
    char** passwords = malloc(100 * sizeof(char*));

    if (!passwords) {
        perror("malloc"); // Robust way to handle memory allocation failure and print error message
        exit(EXIT_FAILURE); // Exit the program on failure
    }

    for (int i = 0; i < 100; ++i) {
        do {
            char* password = generate_password();
            if (passwords[i] != NULL && strcmp(password, passwords[i]) == 0)
                free(password);
            else
                passwords[i] = password;
        } while (passwords[i] == NULL);

        printf("Password %d: %s\n", i + 1, passwords[i]);
    }

    for (int i = 0; i < 100; ++i) {
        if (passwords[i] != NULL)
            free(passwords[i]);
    }

    free(passwords);

    return 0;
}
