#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/rand.h>
#include <openssl/evp.h>

#define MAX_PASSWORD_LENGTH 128 // Define magic number as a constant
#define MIN_PASSWORD_LENGTH 8
#define MAX_BITS_PER_LONG 32

// Error codes and messages
typedef enum {
    SUCCESS,
    DEV_RANDOM_ERROR = 1,
    READ_ERROR = 2,
} ErrorCode;

const char* error_messages[READ_ERROR + 1] = {
    "Success",
    "Error accessing /dev/urandom.",
    "Read operation failed."
};

// Function to securely generate a cryptographically secure random number
unsigned int crypto_rand(unsigned int min, unsigned int max) {
    if (max - min < RAND_MAX)
        return (rand() % (max - min)) + min;

    unsigned long random_number = 0;

    for (int i = 0; i < MAX_BITS_PER_LONG; i++) {
        // Generate a random number in the interval [min, max)
        int lower_bits = rand() & 0x7F;
        int higher_bits = rand() & 0x3F;

        // Combine lower and higher bits using bitwise operations
        random_number |= ((unsigned long)lower_bits << (MAX_BITS_PER_LONG - lower_bits)) | (((unsigned long)higher_bits >> (32 - lower_bits)) & ~(~0UL >> lower_bits));
    }

    return random_number;
}

// Function to generate a digest using EVP
int generate_digest(const unsigned char* plaintext, size_t plaintext_len, unsigned char* out, int *out_len) {
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();

    if (!ctx)
        return DEV_RANDOM_ERROR; // Handle error: EVP_MD_CTX_new() failure

    if (EVP_DigestInit_ex(ctx, EVP_sha256(), NULL)) {
        EVP_DigestUpdate(ctx, plaintext, plaintext_len);

        if (EVP_DigestFinal_ex(ctx, out, out_len))
            return SUCCESS;

        EVP_MD_CTX_free(ctx); // Clean up digest context on error
    }

    EVP_MD_CTX_free(ctx);

    return READ_ERROR; // Handle error: EVP_DigestInit_ex() or EVP_DigestFinal_ex()
}

// Function to securely generate a password
int generate_password(unsigned int length, unsigned char* out) {
    if (length < 0)
        return DEV_RANDOM_ERROR;

    int ret = RAND_bytes(out, length);

    if (ret != 1)
        return DEV_RANDOM_ERROR; // Handle error: RAND_bytes() failure

    return SUCCESS;
}

// Function to allocate memory safely
void* safe_allocate(size_t size) {
    void* ptr = malloc(size);

    if (!ptr)
        printf("Error: Out of memory\n");

    return ptr;
}

int main(void) {
    char buffer[256];
    int num_passwords, length;
    unsigned char* passwords = NULL;

    // Get the number of passwords from the user
    while (1) {
        printf("Enter the number of passwords to generate: ");
        if (!fgets(buffer, sizeof(buffer), stdin)) {
            printf("Error reading input\n");
            return 1; // Handle error: fgets() failure
        }

        num_passwords = atoi(buffer);

        if (num_passwords > 0)
            break;

        printf("Invalid number. Please enter a positive integer.\n");
    }

    // Get the length of each password from the user
    while (1) {
        printf("Enter the desired length for each password: ");
        if (!fgets(buffer, sizeof(buffer), stdin)) {
            printf("Error reading input\n");
            return 1; // Handle error: fgets() failure
        }

        length = atoi(buffer);

        if (length > 0)
            break;

        printf("Invalid length. Please enter a positive integer.\n");
    }

    passwords = safe_allocate(num_passwords * length); // Allocate memory for the passwords

    for (int i = 0; i < num_passwords; ++i) {
        unsigned char password[length];

        if (generate_password(length, password)) {
            printf("Error generating password\n");
            return 1; // Handle error: generate_password() failure
        }

        memcpy(&passwords[i * length], password, length);
    }

    printf("Generated Passwords:\n");

    // Print generated passwords
    for (int i = 0; i < num_passwords; ++i) {
        for (unsigned int j = 0; j < length; ++j)
            printf("%c", passwords[i * length + j]);

        printf("\n");
    }

    free(passwords); // Clean up allocated memory

    return 0;
}
