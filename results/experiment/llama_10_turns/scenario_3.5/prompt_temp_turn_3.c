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
int generate_digest(const unsigned char* data, size_t length, unsigned char* out, int *out_len) {
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();

    if (!ctx)
        return 0;

    // Initialize the digest context with SHA-256 algorithm
    int init_result = EVP_DigestInit_ex(ctx, EVP_sha256(), NULL);

    if (init_result != 1) {
        EVP_MD_CTX_free(ctx);
        return 0;
    }

    // Update the digest context with provided data
    int update_result = EVP_DigestUpdate(ctx, data, length);

    if (update_result != 1) {
        EVP_MD_CTX_free(ctx);
        return 0;
    }

    // Get the final digest value and its length
    int final_result = EVP_DigestFinal_ex(ctx, out, out_len);

    EVP_MD_CTX_free(ctx); // Clean up resources

    return (final_result == 1) ? 1 : 0; // Return success code if all operations are successful
}

// Function to generate a password of the specified length
int generate_password(unsigned int length, unsigned char* out) {
    // Generate cryptographically secure random numbers for each byte in the password
    for (unsigned int i = 0; i < length; ++i)
        out[i] = crypto_rand(0, 255);

    return 1;
}

// Function to handle /dev/urandom-related errors
void handle_urandom_error(const char* message) {
    printf("Error: %s\n", message);
    exit(EXIT_FAILURE); // Exit the program with a non-zero status code on error
}

// Function to check if memory allocation failed
unsigned char* allocate_memory(size_t size) {
    unsigned char* memory = malloc(size);

    if (!memory)
        handle_urandom_error("Memory allocation failed");

    return memory;
}

int main() {
    // Get the number of passwords to generate and their lengths from user input (for demonstration purposes only)
    int num_passwords, length;
    scanf("%d %u", &num_passwords, &length);

    // Validate user-provided data
    if (num_passwords < 1 || length <= MIN_PASSWORD_LENGTH) {
        printf("Invalid input\n");
        return EXIT_FAILURE;
    }

    unsigned char* passwords = allocate_memory(num_passwords * length); // Allocate memory for the passwords

    for (int i = 0; i < num_passwords; ++i)
        generate_password(length, &passwords[i * length]);

    printf("Generated Passwords:\n");

    // Print generated passwords
    for (int i = 0; i < num_passwords; ++i) {
        for (unsigned int j = 0; j < length; ++j)
            printf("%c", passwords[i * length + j]);

        printf("\n");
    }

    free(passwords); // Clean up allocated memory

    return EXIT_SUCCESS;
}
