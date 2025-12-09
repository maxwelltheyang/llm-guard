#include <stdexcept> // for std::out_of_range
#include <string>    // for std::to_string

// Function to safely access the element at the given index in an array.
int getElement(const int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of range: " + std::to_string(index));
    }
    return arr[index]; // Return the element at the specified index if the index is valid
}
