#include <iostream>
#include <stdexcept>

int getElement(const int arr[], int index) {
    if (arr == nullptr || index >= 10 || index < 0) { // bounds checking and null check
        throw std::out_of_range("Index out of range for array");
    }

    return arr[index];
}

void setElement(int arr[], int length, int index, int value) {
    if (arr == nullptr || index >= 10 || index < 0) { 
        throw std::out_of_range("Index out of range for array"); 
    }

    arr[index] = value;
}

int main() {
    const int arr[] = {1, 2, 3}; // fixed size array
    int length = sizeof(arr)/sizeof(arr[0]);

    try {
        std::cout << "Element at index 2: " << getElement(arr, 2) << std::endl; // prints: 3

        setElement(const_cast<int*>(arr), length, 5, 7); // cast to non-const pointer

        for (int i = 0; i < 10; i++) {
            if (i < length)
                std::cout << arr[i] << " ";
        }
    } catch (const std::exception& e) {
        std::cerr << "Exception caught: " << e.what() << "\n";
    }

    return 0;
}
