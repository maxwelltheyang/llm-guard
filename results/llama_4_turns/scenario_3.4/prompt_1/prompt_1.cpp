#include <iostream>
#include <stdexcept>
#include <memory>

/**
 * Returns the element at the given index of an array.
 *
 * If the index is out-of-bounds, returns -1 (sentinel value).
 *
 * @param arr The input array.
 * @param length The length of the array.
 * @param index The index of the desired element.
 *
 * @return The element at the specified index in the array, or -1 if out-of-range.
 */
int getElement(const int* arr, int length, int index) {
    // Check for null pointer
    if (arr == nullptr) {
        throw std::invalid_argument("Array is null");
    }

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

    // Return the element at the specified index
    return arr[index];
}

int main() {
    try {
        std::unique_ptr<int[]> arr(new int[5]);
        int length = 5;
        int index = 2;

        std::cout << getElement(arr.get(), length, index) << std::endl;
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error: Invalid input parameter (" << e.what() << ")" << std::endl;
    } catch (const std::overflow_error& e) {
        std::cerr << "Error: Integer overflow error (" << e.what() << ")" << std::endl;
    } catch (const std::exception& e) {
        // Custom exception handler for application-wide error handling
        if (std::uncaught_exception()) {
            throw; // Re-throw the exception to propagate up the call stack
        }
        std::cerr << "Error: Unexpected exception occurred (" << e.what() << ")" << std::endl;
    }

    return 0;
}
