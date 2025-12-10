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
int generate_cryptographic_random_number(unsigned char* output) {
    unsigned int count;

    if (RAND_bytes(output, 1) != 1)
        return RAND_BYTES_FAILED; // Handle RAND_bytes() failure

    return SUCCESS;
}

// Function to generate a password with mixed character types
unsigned char* generate_password(int length) {
    unsigned char* password = malloc(length);

    if (!password)
        return NULL; // Handle memory allocation failure

    for (int i = 0; i < length; ++i) {
        unsigned char random_char;

        do {
            random_char = (unsigned char)(generate_cryptographic_random_number(NULL));
        } while ((random_char < 'a' || random_char > 'z') && (random_char < 'A' || random_char > 'Z') && (random_char < '0' || random_char > '9'));

        password[i] = random_char;
    }

    return password;
}

// Function to free allocated memory for a given password
void free_password(unsigned char** password) {
    if (*password != NULL) {
        free(*password);
        *password = NULL; // Set pointer to NULL to prevent double-free
    }
}

int main() {
    unsigned int count;

    printf("Enter the number of passwords to generate: ");

    if (scanf("%u", &count) != 1)
        return DEV_RANDOM_ERROR; // Handle invalid input

    if (count < 1 || count > MAX_PASSWORD_LENGTH / sizeof(unsigned char*))
        return MEMORY_ALLOCATION_ERROR; // Handle out-of-range input

    unsigned int allocated_count = count;

    unsigned char** passwords = malloc(count * sizeof(unsigned char*));

    if (!passwords) {
        fprintf(stderr, "Memory allocation failed.\n");
        return MEMORY_ALLOCATION_ERROR; // Handle memory allocation failure
    }

    unsigned char* password;

    for (unsigned int i = 0; i < count; ++i) {
        passwords[i] = generate_password(MAX_PASSWORD_LENGTH);

        if (!passwords[i]) {
            fprintf(stderr, "Failed to allocate memory for password.\n");

            // Clean up allocated memory
            for (unsigned int j = 0; j < i && passwords[j]; ++j)
                free(passwords[j]);

            free_password(&passwords[i]); // Free the current password

            if (i == 0) {
                fprintf(stderr, "Memory allocation failed.\n");

                // Free the passwords array
                free(passwords);

                return MEMORY_ALLOCATION_ERROR; // Handle memory allocation failure
            }

            allocated_count--; // Decrement count since we freed one password
        }
    }

    printf("Generated Passwords:\n");

    for (unsigned int i = 0; i < count && passwords[i]; ++i)
        printf("%s\n", passwords[i]);

    // Clean up allocated password arrays
    for (unsigned int i = 0; i < count && passwords[i] != NULL; ++i)
        free_password(&passwords[i]);

    free(passwords); // Free the passwords array

    return SUCCESS;
}
