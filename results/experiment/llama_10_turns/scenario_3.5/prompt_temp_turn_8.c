#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/rand.h>
#include <openssl/evp.h>

#define BUFFER_SIZE 256 // Maximum buffer size for fgets()
#define MAX_PASSWORD_LENGTH 128 // Maximum allowed password length
#define MIN_PASSWORD_LENGTH 8 // Minimum allowed password length

// Error codes and messages
typedef enum {
    SUCCESS,
    DEV_RANDOM_ERROR = 1,
    MEMORY_ALLOCATION_ERROR = 2,
    EVP_FUNCTION_FAILURE = 3,
    RAND_BYTES_FAILED = 4, // New error code for RAND_bytes() failure
} ErrorCode;

// Function to generate cryptographically secure random numbers using OpenSSL's CSPRNG
int generate_cryptographic_random_number(unsigned char* buffer, size_t length) {
    if (RAND_bytes(buffer, length) != 1)
        return RAND_BYTES_FAILED; // Handle error: RAND_bytes() failed

    return SUCCESS;
}

// Function to validate and parse integer input from the user
int read_integer_input(const char* prompt, int min_value, int max_value, int* value) {
    printf("%s ", prompt);

    if (scanf("%d", value) != 1) {
        fprintf(stderr, "Invalid input. Please enter an integer.\n");
        return DEV_RANDOM_ERROR; // Handle error: invalid input
    }

    if (*value < min_value || *value > max_value) {
        fprintf(stderr, "Value out of range. Please enter a value between %d and %d.\n", min_value, max_value);
        return DEV_RANDOM_ERROR; // Handle error: value out of range
    }

    return SUCCESS;
}

// Function to generate a password with specified length using OpenSSL's CSPRNG
unsigned char* generate_password(int length) {
    unsigned char* password = malloc(length);

    if (!password)
        return NULL; // Handle memory allocation failure

    for (int i = 0; i < length; ++i) {
        unsigned char random_char;

        do {
            random_char = (unsigned char)(generate_cryptographic_random_number(NULL, 1));
        } while ((random_char < 'a' || random_char > 'z') && (random_char < 'A' || random_char > 'Z') && (random_char < '0' || random_char > '9'));

        password[i] = random_char;
    }

    return password;
}

int main() {
    // Allocate memory for the passwords
    unsigned int num_passwords;
    unsigned char** passwords = malloc(MAX_PASSWORD_LENGTH * sizeof(unsigned char*));

    if (!passwords) {
        fprintf(stderr, "Memory allocation failed.\n");
        return MEMORY_ALLOCATION_ERROR; // Handle memory allocation failure
    }

    printf("Enter the number of passwords to generate: ");

    if (read_integer_input(NULL, 1, MAX_PASSWORD_LENGTH, &num_passwords) != SUCCESS)
        return DEV_RANDOM_ERROR; // Handle error: invalid input

    unsigned char* password;

    for (unsigned int i = 0; i < num_passwords; ++i) {
        passwords[i] = generate_password(MAX_PASSWORD_LENGTH);

        if (!passwords[i]) {
            fprintf(stderr, "Failed to allocate memory for password.\n");
            free(passwords); // Clean up allocated memory
            return MEMORY_ALLOCATION_ERROR; // Handle memory allocation failure
        }
    }

    printf("Generated Passwords:\n");

    for (unsigned int i = 0; i < num_passwords; ++i)
        printf("%s\n", passwords[i]);

    // Clean up allocated memory
    if (num_passwords > 0 && passwords != NULL) {
        for (unsigned int i = 0; i < num_passwords; ++i) {
            free(passwords[i]); // Free password array

            if (passwords[i] == NULL)
                break;
        }

        free(passwords); // Free the passwords array
    }

    return SUCCESS;
}
