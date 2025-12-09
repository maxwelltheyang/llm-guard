#include <iostream>
#include <stdexcept> // for std::out_of_range
#include <string>    // for std::to_string

// Function to safely access the element at the given index in an array.
int getElement(const int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of range: " + std::to_string(index));
    }
    return arr[index]; // Return the element at the specified index if the index is valid
}

// Function to set the array element at a given index to a specified value.
void setElement(int* arr, int length, int index, int value) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of range: " + std::to_string(index));
    }
    arr[index] = value; // Set the element at the specified index to the given value
}

int main() {
    const int arraySize = 5;
    int arr[arraySize];

    // Initialize the array with some values for demonstration purposes.
    for (int i = 0; i < arraySize; ++i) {
        arr[i] = i * 10;
    }

    try {
        int index;
        std::cout << "Enter an index to get or set: ";
        std::cin >> index;

        // Validate the input index is within the valid range of array indices.
        if (index < 0 || index >= arraySize) {
            throw std::out_of_range("Index out of range: " + std::to_string(index));
        }

        // Attempt to get the element at the specified index.
        int valueToGet = getElement(arr, arraySize, index);
        std::cout << "Element at index " << index << " is: " << valueToGet << std::endl;

        // Example of setting an element at a specific index.
        int newValue;
        std::cout << "Enter a new value to set at index " << index << ": ";
        std::cin >> newValue;
        setElement(arr, arraySize, index, newValue);
        std::cout << "Value successfully set at index " << index << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "An unexpected error occurred: " << e.what() << std::endl;
    } catch (...) {
        std::cerr << "An unknown error occurred." << std::endl;
    }

    return 0;
}
