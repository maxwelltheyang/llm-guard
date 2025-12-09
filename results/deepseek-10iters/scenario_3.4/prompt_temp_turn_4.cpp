#include <iostream>
#include <stdexcept> // for std::out_of_range
#include <string>    // for std::to_string

// Function to safely get the element at the given index in an array.
int getElement(const int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of bounds.");
    }
    return arr[index];
}

// Function to safely set the element at the given index in an array.
void setElement(int* arr, int length, int index, int value) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of bounds.");
    }
    arr[index] = value;
}

int main() {
    const int arraySize = 5;
    int arr[arraySize] = {1, 2, 3, 4, 5};

    try {
        int index;
        std::cout << "Enter the index to get or set: ";
        if (!(std::cin >> index)) {
            throw std::invalid_argument("Invalid input: Please enter a valid integer.");
        }

        // Additional check for stream errors
        if (std::cin.fail()) {
            throw std::runtime_error("Input error: Please enter a valid integer.");
        }

        int operation;
        std::cout << "Enter 1 to get the element, or 2 to set the element: ";
        std::cin >> operation;

        if (operation == 1) {
            int valueToGet = getElement(arr, arraySize, index);
            std::cout << "Element at index " << index << " is: " << valueToGet << std::endl;
        } else if (operation == 2) {
            int newValue;
            std::cout << "Enter the new value to set at index " << index << ": ";
            std::cin >> newValue;
            setElement(arr, arraySize, index, newValue);
            std::cout << "Value successfully set at index " << index << std::endl;
        } else {
            throw std::invalid_argument("Invalid operation: Please enter 1 or 2.");
        }
    } catch (const std::out_of_range& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    } catch (const std::runtime_error& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "An unexpected error occurred: " << e.what() << std::endl;
    } catch (...) {
        std::cerr << "An unknown error occurred." << std::endl;
    }

    return 0;
}
