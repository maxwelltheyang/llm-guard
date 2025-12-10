#include <iostream>
#include <stdexcept>
#include <vector>

class IndexError : public std::runtime_error {
public:
    IndexError(const std::string& message) : std::runtime_error(message) {}
};

/**
 * Returns the element at the given index of an array.
 *
 * @param arr The input vector.
 * @param index The index of the desired element.
 * @return The element at the specified index, or throws an IndexError if out of bounds.
 */
long getElement(const std::vector<long>& vec, int index) {
    // Check if the index is within the bounds of the array
    if (index < 0 || static_cast<size_t>(index) >= vec.size()) {
        throw IndexError("Index out of range");
    }

    // If the index is valid, return the element at that position
    return vec[index];
}

/**
 * Sets the array element at index to the given value.
 *
 * @param arr The input vector.
 * @param length The size_t of the array. Should match the actual size of the vector for safety.
 * @param index The index where the new value will be stored.
 * @param value The new value for the specified index.
 */
void setElement(std::vector<long>& vec, int index, long value) {
    // Check if the index is within the bounds of the array
    if (index < 0 || static_cast<size_t>(index) >= vec.size()) {
        throw IndexError("Index out of range");
    }

    // Reserve enough capacity to avoid reallocation when setting an element beyond the current size
    if (static_cast<size_t>(index) > vec.capacity()) {
        vec.reserve(index + 1);
    }

    // Check for integer overflow before storing the new value
    if (-2147483648 <= value && value <= 2147483647) {
        vec[index] = value;
    } else {
        std::cerr << "Warning: Value is too large for type long and was not stored. Overflow prevented." << '\n';
    }
}

int main() {
    try {
        // Reserve enough capacity to handle elements beyond the initial size
        std::vector<long> arr(5);
        arr.reserve(10); // Set a higher reserve value if needed

        std::cout << getElement(arr, 2) << std::endl; // Output: 0

        setElement(arr, 0, 2147483648);

        for (long i : arr) {
            std::cout << i << " ";
        }
    } catch (const IndexError& e) {
        std::cerr << "Error: " << e.what() << '\n';
    }

    return 0;
}
