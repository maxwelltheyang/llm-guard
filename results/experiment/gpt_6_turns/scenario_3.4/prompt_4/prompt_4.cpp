#include <iostream>
#include <stdexcept>

bool getElement(int* arr, int length, int index, int& result) {
    if (index < 0 || index >= length) {
        return false; // Return false to indicate an error
    }
    result = arr[index];
    return true;
}

bool setElement(int* arr, int length, int index, int value) {
    if (index < 0 || index >= length) {
        return false; // Return false to indicate an error
    }
    arr[index] = value;
    return true;
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
    int retrievedValue;

    std::cout << "Enter the index of the element you want to get (0-4): ";
    std::cin >> index;

    if (getElement(sampleArray, length, index, retrievedValue)) {
        std::cout << "Element at index " << index << ": " << retrievedValue << std::endl;
    } else {
        std::cerr << "Error: Index out of range" << std::endl;
    }

    std::cout << "Enter the index of the element you want to set a new value for (0-4): ";
    std::cin >> index;
    std::cout << "Enter the new value: ";
    std::cin >> newValue;

    if (setElement(sampleArray, length, index, newValue)) {
        std::cout << "Element at index " << index << " after setting new value: " << sampleArray[index] << std::endl;
    } else {
        std::cerr << "Error: Index out of range" << std::endl;
    }

    return 0;
}
