#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <ctype.h>

char* generate_password() {
    static char password[9]; // 8 characters + null terminator
    for (int i = 0; i < 8; i++) {
        int random_number = rand() % 26; // Generate a number between 0 and 25
        char c = 'A' + random_number; // Convert to uppercase letter
        password[i] = c;
    }
    password[8] = '\0'; // Null-terminate the string
    return password;
}
