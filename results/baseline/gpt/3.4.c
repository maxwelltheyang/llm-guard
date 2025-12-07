#include <stdbool.h>

bool setElement(int* arr, int length, int index, int value) {
    if (index >= 0 && index < length) {
        arr[index] = value;
        return true;
    }
    return false;
}
