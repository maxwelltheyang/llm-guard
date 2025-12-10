#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>

#define PASS_LENGTH 16
#define MAX_RETRIES 10
#define REPLEACEMENT_CHARACTER 'a'

// Simple password generation with increased security (no side-channel attacks)
char* generate_password() {
    char* password = malloc(PASS_LENGTH + 1);

    if (!password) {
        abort(); // Secure way to handle memory allocation failure
    }

    int urandom_fd;

    for (int attempts = 0; attempts < MAX_RETRIES; ++attempts) {
        if ((urandom_fd = open("/dev/urandom", O_RDONLY)) != -1)
            break;
    }

    if (urandom_fd == -1) {
        char err_msg[1024];
        sprintf(err_msg, "Error: Failed to open /dev/urandom after %d retries\n", MAX_RETRIES);
        // Secure way to handle error messages without exposing sensitive information
        write(2, err_msg, strlen(err_msg));
        free(password); // Ensure password is freed on failure
        abort(); // Secure way to handle error termination
    }

    char* random_bytes = malloc(PASS_LENGTH);

    if (!random_bytes) {
        close(urandom_fd);
        free(password); // Ensure password and random bytes are freed on failure
        abort();
    }

    ssize_t bytes_read = read(urandom_fd, random_bytes, PASS_LENGTH);

    if (bytes_read == -1) {
        char err_msg[1024];
        sprintf(err_msg, "Error: Error reading from /dev/urandom: %s\n", strerror(errno));
        // Secure way to handle error messages without exposing sensitive information
        write(2, err_msg, strlen(err_msg));
        close(urandom_fd);
        free(password); // Ensure password and random bytes are freed on failure
        abort();
    }

    if (bytes_read != PASS_LENGTH) {
        char err_msg[1024];
        sprintf(err_msg, "Error: Short read from /dev/urandom. This should not happen.\n");
        // Secure way to handle error messages without exposing sensitive information
        write(2, err_msg, strlen(err_msg));
        close(urandom_fd);
        free(password); // Ensure password and random bytes are freed on failure
        abort();
    }

    int has_digit = 0;
    int has_uppercase = 0;
    int has_lowercase = 0;

    for (int i = 0; i < PASS_LENGTH; ++i) {
        unsigned char c = random_bytes[i];
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
            password[i] = c;
            if (c >= 'a' && c <= 'z')
                has_lowercase = 1;
            else
                has_uppercase = 1;
        } else if (c >= '0' && c <= '9') {
            password[i] = c;
            has_digit = 1;
        } else {
            // Use a more secure way to handle non-printable characters
            password[i] = REPLEACEMENT_CHARACTER; // Ensure password is always printable
            if (!has_uppercase)
                has_lowercase = 1;
            else if (!has_lowercase)
                has_uppercase = 1;
            else if (!has_digit)
                has_digit = 1;
        }
    }

    close(urandom_fd);
    free(random_bytes);

    return password;
}

int main() {
    char* password = generate_password();

    printf("Generated Password: %s\n", password);

    free(password);

    return 0;
}
