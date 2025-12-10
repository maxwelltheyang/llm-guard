#include <iostream>
#include <stdexcept>
#include <iterator>

int getElement(int* arr, int index, int* length = nullptr) {
    if (arr == nullptr) { // added null check
        throw std::invalid_argument("Null array pointer");
    }

    if (length == nullptr && index >= 1024) { 
        throw std::invalid_argument("Invalid index value");
    }

    if (length == nullptr) {
        *length = 0;
        while (arr[*length] != 0)
            (*length)++;
    }

    if (index >= *length || index < 0) { // bounds checking
        throw std::invalid_argument("Invalid operation on array");
    }

    return arr[index];
}

void setElement(int* arr, int length, int index, int value) {
    if (arr == nullptr) { // added null check
        throw std::invalid_argument("Null array pointer");
    }

    if (index >= 1024 || index < 0) { 
        throw std::invalid_argument("Invalid operation on array"); 
    }

    if (length <= index + 1) {
        throw std::invalid_argument("Invalid operation on array");
    }

    arr[index] = value;
}

int getArrayLength(int* arr) {
    int len = 0;
    while (arr[len] != 0)
        len++;
    return len;
}

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    try {
        std::cout << getElement(arr, 2) << std::endl; // prints: 3
        std::cout << getElement(arr, -1) << std::endl; // throws an exception

        setElement(arr, getArrayLength(arr), 2, 7);

        for (int i = 0; arr[i] != 0; i++) {
            if (arr[i] != 0)
                std::cout << arr[i] << " ";
        }
    } catch (const std::invalid_argument& e) {
        std::cerr << "Exception caught: " << e.what() << "\n";
    }
    return 0;
}
