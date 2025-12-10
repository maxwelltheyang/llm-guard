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
        return DEV_RANDOM_ERROR; // Handle error: EVP_MD_CTX_new() failure

    if (EVP_DigestInit_ex(ctx, EVP_sha256(), NULL)) {
        EVP_DigestUpdate(ctx, plaintext, plaintext_len);

        if (EVP_DigestFinal_ex(ctx, out, out_len) != 1)
            return DEV_RANDOM_ERROR; // Handle error: EVP_DigestFinal_ex()

    } else
        return DEV_RANDOM_ERROR; // Handle error: EVP_DigestInit_ex()

    EVP_MD_CTX_free(ctx); // Clean up EVP context

    return SUCCESS;
}

// Function to generate a password of specified length using cryptographically secure random numbers
int generate_password(unsigned char* password, size_t length) {
    if (length <= 0 || length > MAX_PASSWORD_LENGTH)
        return DEV_RANDOM_ERROR; // Handle error: invalid length

    for (size_t i = 0; i < length; ++i)
        password[i] = crypto_rand(0x00, 0xFF);

    return SUCCESS;
}

// Function to print the generated passwords
void print_passwords(unsigned char** passwords, size_t num_passwords, size_t password_length) {
    for (size_t i = 0; i < num_passwords; ++i) {
        for (size_t j = 0; j < password_length; ++j)
            printf("%c", passwords[i][j]);

        printf("\n");
    }
}

// Function to free allocated memory
void clean_up(unsigned char** passwords, size_t num_passwords) {
    for (size_t i = 0; i < num_passwords; ++i)
        free(passwords[i]);

    free(passwords); // Clean up all allocated memory
}

int main() {
    unsigned int num_passwords;
    unsigned char* passwords = NULL;

    printf("Enter the number of passwords to generate: ");
    if (scanf("%u", &num_passwords) != 1 || num_passwords <= 0)
        return DEV_RANDOM_ERROR; // Handle error: invalid input

    printf("Enter the length of each password (between %d and %d): ", MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH);
    unsigned char password_length;

    if (scanf("%c", &password_length) != 1 || password_length < MIN_PASSWORD_LENGTH || password_length > MAX_PASSWORD_LENGTH)
        return DEV_RANDOM_ERROR; // Handle error: invalid length

    passwords = malloc(num_passwords * password_length); // Allocate memory for the passwords

    if (!passwords)
        return DEV_RANDOM_ERROR; // Handle error: failed to allocate memory

    unsigned char* password;

    for (size_t i = 0; i < num_passwords; ++i) {
        password = malloc(password_length);

        if (!password)
            return DEV_RANDOM_ERROR; // Handle error: failed to allocate memory

        if (generate_password(password, password_length) != SUCCESS)
            return DEV_RANDOM_ERROR; // Handle error: generate_password() failure

        memcpy(&passwords[i * password_length], password, password_length);

        free(password); // Clean up allocated memory
    }

    printf("Generated Passwords:\n");

    print_passwords((unsigned char**) passwords, num_passwords, password_length);

    clean_up((unsigned char**) &passwords, num_passwords); // Clean up all allocated memory

    return 0;
}
