#include <stdexcept> // for std::out_of_range
#include <cstddef>   // for std::size_t

// Function to return the element at the given index of an array
int getElement(const int* arr, std::size_t length, std::size_t index) {
    if (index >= length) {
        throw std::out_of_range("Index out of bounds");
    }
    return arr[index];
}
