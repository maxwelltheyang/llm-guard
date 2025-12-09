#include <iostream>
#include <stdexcept>

int getElement(int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index is out of bounds");
    }
    return arr[index];
}

void setElement(int* arr, int length, int index, int value) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index is out of bounds");
    }
    arr[index] = value;
}

int main() {
    int arr[] = {10, 20, 30, 40, 50};
    int length = sizeof(arr) / sizeof(arr[0]);

    try {
        int index = 2; // Example index to get and set
        int element = getElement(arr, length, index);
        std::cout << "Element at index " << index << " is " << element << std::endl;

        // Setting new value at the index
        int newValue = 99;
        setElement(arr, length, index, newValue);
        std::cout << "Element at index " << index << " after setting new value is " << arr[index] << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << e.what() << std::endl;
    }

    return 0;
}
