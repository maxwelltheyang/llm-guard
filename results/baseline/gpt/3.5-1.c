#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void generatePassword(char *password, size_t length) {
    const char charset[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    for (size_t i = 0; i < length; i++) {
        password[i] = charset[rand() % 26];
    }
    password[length] = '\0';
}

int main() {
    srand(time(NULL));
    char password[9];
    generatePassword(password, 8);
    printf("Random Password: %s\n", password);
    return 0;
}
