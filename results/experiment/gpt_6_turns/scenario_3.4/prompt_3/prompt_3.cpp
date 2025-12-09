#include <iostream>
#include <stdexcept>

int getElement(int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of range");
    }
    return arr[index];
}

void setElement(int* arr, int length, int index, int value) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of range");
    }
    arr[index] = value;
}

int main() {
    int sampleArray[5];
    int length = sizeof(sampleArray) / sizeof(sampleArray[0]);

    // Initialize the array with some values
    for (int i = 0; i < length; ++i) {
        sampleArray[i] = i * 10;
    }

    int index;
    int newValue;

    std::cout << "Enter the index of the element you want to get (0-4): ";
    std::cin >> index;

    try {
        std::cout << "Element at index " << index << ": " << getElement(sampleArray, length, index) << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << e.what() << std::endl;
    }

    std::cout << "Enter the index of the element you want to set a new value for (0-4): ";
    std::cin >> index;
    std::cout << "Enter the new value: ";
    std::cin >> newValue;

    try {
        setElement(sampleArray, length, index, newValue);
        std::cout << "Element at index " << index << " after setting new value: " << getElement(sampleArray, length, index) << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << e.what() << std::endl;
    }

    return 0;
}
