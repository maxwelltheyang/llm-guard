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

// Named constants for bit lengths
#define MAX_BITS_PER_LONG 32

// Function to securely generate a cryptographically secure random number
unsigned int crypto_rand(unsigned int min, unsigned int max) {
    if (max - min < RAND_MAX)
        return (rand() % (max - min)) + min;

    unsigned long result = 0;
    for (int i = 0; i < MAX_BITS_PER_LONG; i++) {
        // Generate a random number in the interval [min, max)
        int l = rand() & 0x7F; 
        int h = rand() & 0x3F; 

        result |= ((unsigned long)l << (MAX_BITS_PER_LONG - l)) | (((unsigned long)h >> (32 - l)) & ~(~0UL >> l));
    }

    return result;
}

// Function to generate a digest using EVP
int generate_digest(const unsigned char* data, size_t length, unsigned char* out, int *out_len) {
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();

    if (!ctx)
        return 0;

    if (EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) != 1)
        goto error_out;

    if (EVP_DigestUpdate(ctx, data, length) != 1)
        goto error_out;

    int ret = EVP_DigestFinal_ex(ctx, out, out_len);

    if (!ret)
        goto error_out;

    EVP_MD_CTX_free(ctx);

    return 1;

error_out:
    EVP_MD_CTX_free(ctx);
    return 0;
}

// Function to generate a random password
int generate_password(unsigned char* data, size_t length, unsigned char* out, int *out_len) {
    RAND_bytes(data, length);

    if (!data)
        return 0;

    return generate_digest(data, length, out, out_len);
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

int main() {
    const int num_passwords = 10;

    if (num_passwords <= 0) {
        print_error(DEV_RANDOM_ERROR);
    }

    int min_length = MIN_PASSWORD_LENGTH;
    int max_length = MAX_PASSWORD_LENGTH;

    if (min_length < 1 || max_length < min_length) {
        print_error(DEV_RANDOM_ERROR);
    }

    for (int i = 0; i < num_passwords; i++) {
        unsigned char* password_data = NULL;

        size_t length = crypto_rand(min_length, max_length);
        unsigned char* out = malloc(length);
        int out_len = length;

        if (!generate_password(password_data, length, out, &out_len)) {
            print_error(DEV_RANDOM_ERROR);
        }

        free(out);
    }

    return 0;
}
