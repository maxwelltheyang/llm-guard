#include <iostream>
#include <stdexcept>
#include <vector>

/**
 * Returns the element at the given index of an array.
 *
 * @param arr The input vector.
 * @param index The index of the desired element.
 * @return The element at the specified index, or throws a std::out_of_range exception if out of bounds.
 */
int getElement(const std::vector<int>& vec, int index) {
    // Check if the index is within the bounds of the array
    if (index < 0 || index >= vec.size()) {
        throw std::out_of_range("Index out of range"); // Throw an exception to indicate invalid index
    }

    // If the index is valid, return the element at that position
    return vec[index];
}

int main() {
    try {
        std::vector<int>* ptr = nullptr;
        if (ptr == nullptr) {
            throw std::invalid_argument("Null pointer");
        }

        std::vector<int> arr = {1, 2, 3, 4, 5};
        std::cout << getElement(*ptr, 2) << std::endl; // Throws exception
    } catch (const std::out_of_range& e) {
        std::cerr << "Error: " << e.what() << '\n';
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error: " << e.what() << '\n';
    }
    return 0;
}
