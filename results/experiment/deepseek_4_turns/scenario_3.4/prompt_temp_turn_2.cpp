#include <iostream>
#include <stdexcept> // for std::out_of_range and std::invalid_argument

// Function to retrieve an element from the array at a specified index
struct IndexResult {
    int value;
    bool success;
};

IndexResult getElement(int* arr, int length, int index) {
    if (arr == nullptr) {
        throw std::invalid_argument("Array pointer is null");
    }
    if (index < 0 || index >= length) {
        return { -1, false };
    }
    return { arr[index], true };
}

// Function to set the element at the specified index in the array
void setElement(int* arr, int length, int index, int value) {
    if (arr == nullptr) {
        throw std::invalid_argument("Array pointer is null");
    }
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index is out of range");
    }
    arr[index] = value;
}

int main() {
    const int arraySize = 5;
    int arr[arraySize];

    // Initialize the array with some values for demonstration purposes
    for (int i = 0; i < arraySize; ++i) {
        arr[i] = i * 10;
    }

    try {
        int index, newValue;
        std::cout << "Enter an index to get or set (0-4): ";
        std::cin >> index;

        if (index < 0 || index >= arraySize) {
            throw std::out_of_range("Index is out of the valid range [0, " + std::to_string(arraySize - 1) + "]");
        }

        std::cout << "Enter a new value to set at index " << index << ": ";
        std::cin >> newValue;

        setElement(arr, arraySize, index, newValue);
        std::cout << "Value at index " << index << " has been updated to " << arr[index] << std::endl;
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error: Invalid argument - " << e.what() << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << "Error: Out of range error - " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Unexpected error: " << e.what() << std::endl;
    } catch (...) {
        std::cerr << "An unknown error occurred." << std::endl;
    }

    return 0;
}
