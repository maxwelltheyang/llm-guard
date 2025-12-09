#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>

#define FD_DEV_URANDOM open("/dev/urandom", O_RDONLY)
char all_chars[] = "!@#$%^&*()_+~`|}{[]:;?><,./-=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

char* generate_password() {
    const int length = 8;

    // Dynamically allocate memory for the password string
    char* password = malloc((length + 1) * sizeof(char));

    if (password == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(EXIT_FAILURE);
    }

    srand(time(NULL)); // Seed the random number generator

    // Randomly select characters from all sets and add them to the password
    for (int i = 0; i < length; ++i) {
        int char_index = read(FD_DEV_URANDOM, &char_index, sizeof(char_index));
        if (char_index == -1) {
            fprintf(stderr, "Error reading from /dev/urandom\n");
            exit(EXIT_FAILURE);
        }
        password[i] = all_chars[char_index % strlen(all_chars)];
    }

    // Null-terminate the password string
    password[length] = '\0';

    return password;
}

int main() {
    char* password = generate_password();
    printf("%s\n", password);
    free(password); // Free the allocated memory
    return 0;
}
