#include <iostream>
#include <limits>

void setElement(int* arr, int size, int index, int newValue) {
    if (index < 0 || index >= size) {
        throw std::out_of_range("Index out of range.");
    }
    arr[index] = newValue;
}

int getElement(const int* arr, int size, int index) {
    if (index < 0 || index >= size) {
        throw std::out_of_range("Index out of range.");
    }
    return arr[index];
}

int main() {
    const int arraySize = 5;
    int arr[arraySize] = {1, 2, 3, 4, 5};

    try {
        int index, newValue;

        // Validate and get the index input
        while (true) {
            std::cout << "Enter an index to get or set (0-4): ";
            if (!(std::cin >> index)) {
                std::cin.clear(); // clear the error flag
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // discard invalid input
                std::cout << "Invalid input. Enter a valid integer index between 0 and " << (arraySize - 1) << ": ";
            } else if (index < 0 || index >= arraySize) {
                std::cout << "Index out of range. Please enter an index between 0 and " << (arraySize - 1) << ": ";
            } else {
                break;
            }
        }

        // Validate and get the new value input
        while (true) {
            std::cout << "Enter a new value to set at index " << index << ": ";
            if (!(std::cin >> newValue)) {
                std::cin.clear(); // clear the error flag
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // discard invalid input
                std::cout << "Invalid input. Please enter a numeric value: ";
            } else {
                break;
            }
        }

        // Perform the operation based on user choice (get or set)
        char operation;
        std::cout << "Do you want to get or set the element at index " << index << "? (g/s): ";
        std::cin >> operation;

        if (operation == 'g') {
            int value = getElement(arr, arraySize, index);
            std::cout << "Value at index " << index << " is: " << value << std::endl;
        } else if (operation == 's') {
            setElement(arr, arraySize, index, newValue);
            std::cout << "Value at index " << index << " has been updated to " << arr[index] << std::endl;
        } else {
            std::cout << "Invalid operation. Please enter 'g' for get or 's' for set." << std::endl;
        }
    } catch (const std::out_of_range& e) {
        std::cerr << "Error: Out of range error - " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Unexpected error: " << e.what() << std::endl;
    }

    return 0;
}
