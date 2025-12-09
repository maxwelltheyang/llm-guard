#include <iostream>

/**
 * Returns the element at the specified index from the given array.
 *
 * @param arr The input array.
 * @param length The length of the array.
 * @param index The index to retrieve the element at (0-based).
 * @return The element at the specified index, or 0 if out of bounds.
 */
int getElement(int* arr, int length, int index) {
    // Check if the index is within the valid range
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of bounds");
    }

    return arr[index];
}

// Example usage:
int main() {
    int arr[] = {1, 2, 3, 4, 5};
    int length = sizeof(arr) / sizeof(arr[0]);
    try {
        std::cout << getElement(arr, length, 2) << std::endl;  // Output: 3
        std::cout << getElement(arr, length, -1) << std::endl; // Throws an exception
    } catch (const std::exception& e) {
        std::cerr << "Exception caught: " << e.what() << '\n';
    }
    return 0;
}
