#include <iostream>
#include <stdexcept> // for std::out_of_range
#include <cstddef>   // for std::size_t

// Function to set the element at the given index of an array
void setElement(int* arr, std::size_t length, std::size_t index, int value) {
    if (index >= length) {
        throw std::out_of_range("Index out of bounds");
    }
    arr[index] = value;
}

int main() {
    const std::size_t arrayLength = 5;
    int myArray[arrayLength];

    // Initialize the array with some values (optional)
    for (std::size_t i = 0; i < arrayLength; ++i) {
        myArray[i] = i * 10;
    }

    try {
        std::cout << "Initial array: ";
        for (std::size_t i = 0; i < arrayLength; ++i) {
            std::cout << myArray[i] << " ";
        }
        std::cout << std::endl;

        // Get user input for the index and value
        std::size_t index;
        int value;
        std::cout << "Enter an index to set: ";
        std::cin >> index;
        std::cout << "Enter a value to set at that index: ";
        std::cin >> value;

        // Set the element at the specified index
        setElement(myArray, arrayLength, index, value);

        std::cout << "Updated array: ";
        for (std::size_t i = 0; i < arrayLength; ++i) {
            std::cout << myArray[i] << " ";
        }
        std::cout << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    } catch (...) {
        std::cerr << "An unexpected error occurred." << std::endl;
    }

    return 0;
}
