#include <iostream>
#include <stdexcept>
#include <vector>

int getElement(int* arr, int index) {
    if (arr == nullptr) { // added null check
        throw std::invalid_argument("Null array pointer");
    }

    int length = 10; // fixed size of the array

    if (index >= length || index < 0) { // bounds checking
        throw std::out_of_range("Index out of range for array");
    }

    return arr[index];
}

int main() {
    int* arr = new int[10]; // fixed size of the array

    try {
        std::cout << "Element at index 2: " << getElement(arr, 2) << std::endl; // prints: 3

        for (int i = 0; i < 10; i++) {
            arr[i] = 7;
        }

        for (int i = 0; i < 10; i++) {
            if (arr[i] != 0)
                std::cout << arr[i] << " ";
        }
    } catch (const std::exception& e) {
        std::cerr << "Exception caught: " << e.what() << "\n";
    }

    delete[] arr;
    return 0;
}
