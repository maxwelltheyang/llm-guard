#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/rand.h>

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

// Function to generate a password
Error generate_password(char** password, int length) {
    // Check for potential resource leak by closing file descriptors within a loop
    FILE* fd = fopen("/dev/urandom", "rb");
    if (!fd)
        return DEV_RANDOM_ERROR; // Return error code instead of printing error message

    unsigned char bytes[length];

    // Read random data from /dev/urandom into the array
    if (fread(bytes, 1, length, fd) != length)
        return READ_ERROR;

    fclose(fd);

    // Generate a cryptographically secure password by hashing the random bytes using SHA-256
    unsigned char hash[SHA256_DIGEST_LENGTH];

    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, bytes, length);
    SHA256_Final(hash, &sha256);

    // Convert hashed password to a string of hexadecimal digits
    *password = (char*)malloc((length * 2 + 1) * sizeof(char));
    for (int i = 0; i < length * 2; ++i)
        (*password)[i] = (hex_table[(hash[i >> 4] & 0x0F)] << 4 | hex_table[hash[i & 0x0F]]) % 10;

    // Null-terminate the password string
    (*password)[length * 2] = '\0';

    return SUCCESS;
}

// Function to generate multiple passwords
Error generate_unique_passwords(int num_passwords, int min_length, int max_length) {
    if (num_passwords < MIN_PASSWORD_LENGTH || min_length > MAX_PASSWORD_LENGTH || max_length > MAX_PASSWORD_LENGTH)
        printf("Warning: Invalid input values. Truncating to valid range.\n");

    for (int i = 0; i < num_passwords; ++i) {
        int length = crypto_rand(min_length, max_length);

        if (!length)
            return DEV_RANDOM_ERROR;

        char* password = malloc(length + 1);

        Error error_code = generate_password(&password, length);

        if (error_code != SUCCESS) {
            free(password); // Free memory allocated for the password string in case of an error

            return error_code;
        }

        printf("%s\n", password);

        free(password); // Free memory allocated for the password string
    }

    return SUCCESS;
}

int main() {
    srand(time(NULL)); // Initialize random number generator

    int num_passwords = 10; // Example value for the number of passwords to generate
    int min_length = MIN_PASSWORD_LENGTH;
    int max_length = MAX_PASSWORD_LENGTH;

    Error error_code = generate_unique_passwords(num_passwords, min_length, max_length);

    if (error_code != SUCCESS) {
        print_error(error_code);

        return 1; // Exit with non-zero status on error
    }

    return 0;
}

// Helper function to convert hexadecimal digits to their corresponding ASCII values
static const char hex_table[] = "0123456789abcdef";
