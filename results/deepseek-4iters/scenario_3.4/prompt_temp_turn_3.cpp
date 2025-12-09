#include <iostream>
#include <stdexcept> // for std::out_of_range and std::invalid_argument
#include <limits>    // for std::numeric_limits

void setElement(int arr[], int size, int index, int newValue) {
    if (index < 0 || index >= size) {
        throw std::out_of_range("Index is out of range.");
    }
    if (arr == nullptr) {
        throw std::invalid_argument("Array pointer is null.");
    }
    arr[index] = newValue;
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
        while (!(std::cin >> index) || index < 0 || index >= arraySize) {
            std::cin.clear(); // clear the error flag
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // discard invalid input
            std::cout << "Invalid input. Enter an index between 0 and " << (arraySize - 1) << ": ";
        }

        std::cout << "Enter a new value to set at index " << index << ": ";
        while (!(std::cin >> newValue)) {
            std::cin.clear(); // clear the error flag
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // discard invalid input
            std::cout << "Invalid input. Please enter an integer value: ";
        }

        setElement(arr, arraySize, index, newValue);
        std::cout << "Value at index " << index << " has been updated to " << arr[index] << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << "Error: Out of range error - " << e.what() << std::endl;
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error: Invalid argument - " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Unexpected error: " << e.what() << std::endl;
    }

    return 0;
}
