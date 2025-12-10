#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/rand.h>
#include <openssl/evp.h>

#define MAX_PASSWORD_LENGTH 128 // Define magic number as a constant
#define MIN_PASSWORD_LENGTH 8
#define BUFFER_SIZE 256
#define MAX_BITS_PER_LONG 32

// Error codes and messages
typedef enum {
    SUCCESS,
    DEV_RANDOM_ERROR = 1,
    MEMORY_ALLOCATION_ERROR = 2,
    EVP_FUNCTION_FAILURE = 3,
} ErrorCode;

// Function to generate cryptographically secure random numbers using OpenSSL's CSPRNG
int generate_cryptographic_random_number(unsigned char* buffer, size_t length) {
    if (RAND_bytes(buffer, length) != 1)
        return EVP_FUNCTION_FAILURE; // Handle error: RAND_bytes() failed

    return SUCCESS;
}

// Function to validate input and convert it to an integer
int read_integer_input(char* buffer, int max_value) {
    if (fgets(buffer, BUFFER_SIZE, stdin) == NULL || strlen(buffer) < 1)
        return DEV_RANDOM_ERROR; // Handle error: fgets() failed

    char* endptr;
    long value = strtol(buffer, &endptr, 10);

    if (endptr == buffer || *endptr != '\0' || value > max_value || value < 0)
        return DEV_RANDOM_ERROR; // Handle error: invalid input or out of range

    return SUCCESS;
}

// Function to generate a password with specified characteristics
int generate_password(unsigned char* password, size_t length) {
    for (size_t i = 0; i < length; ++i) {
        unsigned char random_char;

        if (generate_cryptographic_random_number(&random_char, sizeof(random_char)) != SUCCESS)
            return DEV_RANDOM_ERROR; // Handle error: generate_cryptographic_random_number() failure

        password[i] = random_char;
    }

    return SUCCESS;
}

int main() {
    srand(time(NULL));

    // Read the number of passwords to generate
    char buffer[32];

    if (read_integer_input(buffer, MAX_PASSWORD_LENGTH) != SUCCESS)
        return DEV_RANDOM_ERROR; // Handle error: read_integer_input() failure

    unsigned int num_passwords = atoi(buffer);

    // Read the length of each password
    printf("Enter the length of each password (max %d): ", MAX_PASSWORD_LENGTH);

    if (read_integer_input(buffer, MAX_PASSWORD_LENGTH) != SUCCESS)
        return DEV_RANDOM_ERROR; // Handle error: read_integer_input() failure

    unsigned int password_length = atoi(buffer);

    if (password_length < MIN_PASSWORD_LENGTH || password_length > MAX_PASSWORD_LENGTH)
        return DEV_RANDOM_ERROR; // Handle error: invalid length

    // Allocate memory for the passwords
    unsigned char** passwords = malloc(num_passwords * sizeof(unsigned char*));

    if (!passwords) {
        fprintf(stderr, "Memory allocation failed.\n");
        return MEMORY_ALLOCATION_ERROR;
    }

    unsigned char* password;

    for (unsigned int i = 0; i < num_passwords; ++i) {
        password = malloc(password_length);

        if (!password) {
            fprintf(stderr, "Failed to allocate memory for password.\n");
            free(passwords); // Clean up allocated memory
            return MEMORY_ALLOCATION_ERROR;
        }

        if (generate_password(password, password_length) != SUCCESS)
            return DEV_RANDOM_ERROR; // Handle error: generate_password() failure

        passwords[i] = password;
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
