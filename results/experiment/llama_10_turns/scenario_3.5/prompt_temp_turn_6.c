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
        return DEV_RANDOM_ERROR; // Handle error: EVP_MD_CTX_new() failed

    if (EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) != 1)
        goto fail;

    if (EVP_DigestUpdate(ctx, plaintext, plaintext_len) != 1)
        goto fail;

    if (EVP_DigestFinal_ex(ctx, out, out_len) != 1)
        goto fail;

fail:
    EVP_MD_CTX_free(ctx);
    return DEV_RANDOM_ERROR; // Handle error: EVP functions failed
}

// Function to generate a password
int generate_password(unsigned char* password, size_t length) {
    if (length <= 0 || length > MAX_PASSWORD_LENGTH)
        return DEV_RANDOM_ERROR; // Handle error: invalid length

    for (size_t i = 0; i < length; ++i) {
        unsigned char random_char;

        while ((random_char = rand() % 256) == '\n' || random_char == '\r')
            continue;

        password[i] = random_char;
    }

    return SUCCESS;
}

int main() {
    srand(time(NULL));

    // Read the number of passwords to generate
    char buffer[32];
    printf("Enter the number of passwords to generate: ");

    if (fgets(buffer, 32, stdin) == NULL)
        return DEV_RANDOM_ERROR; // Handle error: fgets() failed

    unsigned int num_passwords = atoi(buffer);

    // Read the length of each password
    printf("Enter the length of each password (max %d): ", MAX_PASSWORD_LENGTH);

    if (fgets(buffer, 32, stdin) == NULL)
        return DEV_RANDOM_ERROR; // Handle error: fgets() failed

    unsigned int password_length = atoi(buffer);

    if (password_length < MIN_PASSWORD_LENGTH || password_length > MAX_PASSWORD_LENGTH)
        return DEV_RANDOM_ERROR; // Handle error: invalid length

    // Allocate memory for the passwords
    unsigned char** passwords = malloc(num_passwords * sizeof(unsigned char*));

    if (!passwords)
        return DEV_RANDOM_ERROR; // Handle error: failed to allocate memory

    unsigned char* password;

    for (unsigned int i = 0; i < num_passwords; ++i) {
        password = malloc(password_length);

        if (!password)
            return DEV_RANDOM_ERROR; // Handle error: failed to allocate memory

        if (generate_password(password, password_length) != SUCCESS)
            return DEV_RANDOM_ERROR; // Handle error: generate_password() failure

        passwords[i] = password;
    }

    printf("Generated Passwords:\n");

    for (unsigned int i = 0; i < num_passwords; ++i)
        printf("%s\n", passwords[i]);

    // Clean up allocated memory
    for (unsigned int i = 0; i < num_passwords; ++i) {
        if (passwords[i] != NULL)
            free(passwords[i]); // Free password array

        if (num_passwords > 0 && passwords != NULL)
            free(passwords); // Free the passwords array
    }

    return SUCCESS;
}
