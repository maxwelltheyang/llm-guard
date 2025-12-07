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
            return -1; // Sentinel value for out-of-range indices
        }
        return arr.get()[index];
    }

    /**
     * Sets a new element at the specified index in the array.
     *
     * @param index The index where to set the new value.
     * @param value The new value to be assigned.
     */
    void setElement(int index, int value) {
        // Check for invalid length
        if (arr.get() == nullptr || arr.get()[index] < 0) {
            throw std::invalid_argument("Invalid index: Negative values not allowed");
        }

        // Assign new value at specified index
        arr.get()[index] = value;
    }
};

int main() {
    ArrayManager manager;

    try {
        int length;
        while (true) {
            std::cout << "Enter array size (must be positive integer): ";
            if (!(std::cin >> length)) {
                SPDLOG_ERROR("Invalid input: Expected a numeric value");
                continue;
            }
            if (length <= 0) {
                SPDLOG_ERROR("Invalid array size: Must be a positive integer");
                continue;
            }

            manager.arr = std::make_unique<int[]>(length);

            for (int index = 0; index < length; ++index) {
                int value;
                while (true) {
                    std::cout << "Enter element at index " << index << " (must be non-negative integer): ";
                    if (!(std::cin >> value)) {
                        SPDLOG_ERROR("Invalid input: Expected a numeric value");
                        continue;
                    }
                    if (value < 0) {
                        SPDLOG_ERROR("Invalid element value: Must be a non-negative integer");
                        continue;
                    }

                    manager.setElement(index, value);
                    break; // Exit inner loop after successful operation
                }

                int retrievedValue = manager.getElement(length, index);
                std::cout << "Element at index " << index << ": " << retrievedValue << std::endl;
            }
        }

    } catch (const std::exception& e) {
        SPDLOG_ERROR("Error: {}", e.what());
        return 1; // Exit with a non-zero status code for error handling
    }

    return 0;
}
