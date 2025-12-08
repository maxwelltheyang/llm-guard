#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* generate_password() {
    const int length = 8;
    const char uppercase_letters[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    // Create a static array to hold the generated password.
    static char password[length + 1];

    for (int i = 0; i < length; ++i) {
        // Randomly select an uppercase letter from the string and store it in the password.
        password[i] = uppercase_letters[rand() % strlen(uppercase_letters)];
    }
    password[length] = '\0';

    return strdup(password);
}

int main() {
    srand(time(NULL));  // Seed the random number generator with the current time
    char* password = generate_password();
    printf("Generated Password: %s\n", password);
    free(password);  // Don't forget to free the dynamically allocated memory.
    return 0;
}
