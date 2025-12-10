#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/rand.h>
#include <openssl/evp.h>

#define MAX_PASSWORD_LENGTH 128 // Define magic number as a constant
#define MIN_PASSWORD_LENGTH 8

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

// Function to generate a cryptographically secure random number
unsigned int crypto_rand(unsigned int min, unsigned int max) {
    if (max - min < RAND_MAX)
        return (rand() % (max - min)) + min;

    unsigned int result = 0;
    while (result < min || result > max) {
        int l = rand() & 0x7F; // Max 7 bits
        int h = rand() & 0x3F; // Max 5 bits

        // Generate a random number in the interval [min, max)
        // This is more efficient and reliable than generating a random long and checking if it's within the range.
        result = (result << l) | ((h >> (32 - l)) & ~(~0U >> l));
    }

    return result;
}

// Function to generate a password using OpenSSL's CSPRNG
Error generate_password(char** password, int length) {
    unsigned char bytes[length];

    // Read random data from /dev/urandom into the array
    RAND_bytes(bytes, length);

    // Generate a cryptographically secure password by hashing the random bytes using Argon2
    EVP_MD_CTX* mdctx;
    const EVP_MD* hash = EVP_get_digestbyname("argon2id");
    if (!hash)
        return DEV_RANDOM_ERROR; // Return error code instead of printing error message

    if ((mdctx = EVP_MD_CTX_new()) == NULL)
        return READ_ERROR;

    if (1 != EVP_DigestInit_ex(mdctx, hash, NULL)) {
        EVP_MD_CTX_free(mdctx);
        return READ_ERROR;
    }

    if (1 != EVP_DigestUpdate(mdctx, bytes, length)) {
        EVP_MD_CTX_free(mdctx);
        return READ_ERROR;
    }

    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int diglen = sizeof(digest);
    if (1 != EVP_DigestFinal_ex(mdctx, digest, &diglen)) {
        EVP_MD_CTX_free(mdctx);
        return READ_ERROR;
    }

    // Free the context
    EVP_MD_CTX_free(mdctx);

    // Convert and copy the hash value to a string
    char* p = malloc(length + 1); // Allocate space for the password and null-terminator
    if (p == NULL)
        return READ_ERROR;

    sprintf(p, "%s", digest);

    // Copy the first 'length' characters of the password string
    memcpy(*password, p, length);

    free(p);

    return SUCCESS;
}

// Function to securely print a password to the console
void print_password(char* password) {
    printf("%s\n", password);

    // Securely free memory after printing
    free(password);
}

int main() {
    int num_passwords = 10; // Example value for the number of passwords to generate
    int min_length = MIN_PASSWORD_LENGTH;
    int max_length = MAX_PASSWORD_LENGTH;

    if (num_passwords <= 0) {
        printf("Error: Invalid number of passwords\n");
        return 1;
    }

    if (min_length > max_length) {
        printf("Error: Invalid password length range\n");
        return 1;
    }

    for (int i = 0; i < num_passwords; i++) {
        char* password = NULL;

        Error error_code = generate_password(&password, crypto_rand(min_length, max_length));

        if (error_code != SUCCESS) {
            print_error(error_code);

            return 1; // Exit with non-zero status on error
        }

        print_password(password);
    }

    return 0;
}

// Helper function to print an error message and exit the program
void print_error(ErrorCode code) {
    switch (code) {
        case DEV_RANDOM_ERROR:
            printf("Error: %s\n", error_messages[code]);
            break;
        default:
            printf("Error: Unknown error occurred\n");
            break;
    }

    // Exit with non-zero status on error
    exit(code);
}
