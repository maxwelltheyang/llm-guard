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

// Function to get the element at a specific index in the array
int getElement(const int* arr, std::size_t length, std::size_t index) {
    if (index >= length) {
        throw std::out_of_range("Index out of bounds");
    }
    return arr[index];
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
            std::cout << getElement(myArray, arrayLength, i) << " ";
        }
        std::cout << std::endl;

        // Get user input for the index and value
        std::size_t index;
        int value;
        std::cout << "Enter an index to set: ";
        if (!(std::cin >> index)) {
            throw std::invalid_argument("Invalid index format");
        }
        std::cout << "Enter a value to set at that index: ";
        if (!(std::cin >> value)) {
            throw std::invalid_argument("Invalid value format");
        }

        // Set the element at the specified index
        setElement(myArray, arrayLength, index, value);

        std::cout << "Updated array: ";
        for (std::size_t i = 0; i < arrayLength; ++i) {
            std::cout << getElement(myArray, arrayLength, i) << " ";
        }
        std::cout << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << "Error: Index out of bounds. " << e.what() << std::endl;
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error: Invalid input format. " << e.what() << std::endl;
    } catch (...) {
        std::cerr << "An unexpected error occurred." << std::endl;
    }

    return 0;
}
