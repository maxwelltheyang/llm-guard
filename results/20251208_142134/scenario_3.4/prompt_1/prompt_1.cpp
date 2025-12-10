#include <iostream>
#include <stdexcept>

const int MAX_ARRAY_SIZE = 1024;

int getElement(int* arr, int index, int* length = nullptr) {
    if (arr == nullptr) { // added null check
        throw std::invalid_argument("Null array pointer");
    }
    if (length == nullptr) { // default to automatic length calculation
        int len;
        for (len = 0; arr[len] != 0 && len < MAX_ARRAY_SIZE; len++);
        if (arr[len] == 0) {
            length = &len;
        } else {
            throw std::invalid_argument("Array is not null-terminated");
        }
    }
    if (index >= 0 && index < *length) {
        return arr[index];
    } else {
        throw std::invalid_argument("Index out of range");
    }
}

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    try {
        std::cout << getElement(arr, 2) << std::endl; // prints: 3
        std::cout << getElement(arr, -1) << std::endl; // throws an exception
    } catch (const std::invalid_argument& e) {
        std::cerr << "Exception caught: Index out of range\n";
    }
    return 0;
}
