#include <iostream>
#include <stdexcept>
#include <spdlog/spdlog.h> // Include logging library (e.g., spdlog)
#include <sstream>

class ArrayManager {
public:
    std::unique_ptr<int[]> arr;

    /**
     * Returns the element at the given index of an array.
     *
     * If the index is out-of-bounds, returns -1 (sentinel value).
     *
     * @param length The length of the array.
     * @param index The index of the desired element.
     *
     * @return The element at the specified index in the array, or -1 if out-of-range.
     */
    int getElement(int length, int index) const {
        // Check for invalid length
        if (length <= 0) {
            throw std::invalid_argument("Invalid array length");
        }

        // Check for integer overflow
        if (length > INT_MAX / sizeof(int)) {
            throw std::overflow_error("Integer overflow: Array size exceeds maximum value");
        }

        // Check if the given index is within the bounds of the array
        if (index < 0 || index >= length) {
            return -1; // Sentinel value for out-of-range index
        }

        // Ensure that the provided length matches the actual array length
        if (length != arr->size()) {
            throw std::invalid_argument("Length mismatch between input and internal state");
        }

        // Return the element at the specified index, accessing through the raw pointer directly
        return (*arr.get())[index];
    }

    /**
     * Sets the array element at index to the given value.
     *
     * @param index The index where the value will be set.
     * @param value The new value for the specified index.
     */
    void setElement(int index, int value) {
        // Check if the given index is within the bounds of the array
        if (index < 0 || index >= arr->size()) {
            throw std::out_of_range("Index out-of-bounds for array");
        }

        (*arr.get())[index] = value;
    }
};

int main() {
    try {
        ArrayManager manager;
        int length = 5;

        manager.arr = std::make_unique<int[]>(length);
        std::cout << "Array created with size: " << length << std::endl;

        // Get an element from the array
        int index, value;
        while (true) {
            std::cout << "Enter an index to get an element (0-" << length - 1 << "): ";
            if (!(std::cin >> index)) { // Input validation for non-numeric input
                SPDLOG_ERROR("Invalid input: Expected a numeric index");
                break;
            }
            if (index >= 0 && index < length) {
                value = manager.getElement(length, index);
                std::cout << "Element at index " << index << ": " << value << std::endl;
                break; // Exit loop after successful operation
            } else {
                SPDLOG_ERROR("Invalid index: Out of range");
            }
        }

        // Set a new element in the array
        while (true) {
            int newValue;
            std::cout << "Enter the index to set (0-" << length - 1 << ") and then the value: ";
            if (!(std::cin >> index)) { // Input validation for non-numeric input
                SPDLOG_ERROR("Invalid input: Expected a numeric index");
                break;
            }
            if (index < 0 || index >= length) {
                SPDLOG_ERROR("Invalid index: Out of range");
            } else {
                std::cout << "Enter the value to set: ";
                if (!(std::cin >> newValue)) { // Input validation for non-numeric input
                    SPDLOG_ERROR("Invalid input: Expected a numeric value");
                    break;
                }
                manager.setElement(index, newValue);
                std::cout << "Value at index " << index << " set to " << newValue << std::endl;
                break; // Exit loop after successful operation
            }
        }

        // Potential integer overflow checking
        if (length > INT_MAX / sizeof(int)) {
            throw std::overflow_error("Integer overflow: Array size exceeds maximum value");
        }
    } catch (const std::exception& e) {
        SPDLOG_ERROR("Error: {}", e.what());
        return 1; // Exit with a non-zero status code for error handling
    }

    return 0;
}
