#include <stdexcept> // for std::out_of_range
#include <cstddef>   // for std::size_t

// Function to set the element at the given index of an array
void setElement(int* arr, std::size_t length, std::size_t index, int value) {
    if (index >= length) {
        throw std::out_of_range("Index out of bounds");
    }
    arr[index] = value;
}
