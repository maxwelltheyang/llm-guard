#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <ctype.h>

char* generate_password() {
    static char password[9]; // 8 characters + null terminator
    for (int i = 0; i < 8; i++) {
        int random_value = rand() % 26;
        password[i] = 'A' + random_value;
    }
    password[8] = '\0'; // Null-terminate the string
    return password;
}
