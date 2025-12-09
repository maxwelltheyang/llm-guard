#include <stdexcept> // for std::out_of_range
#include <string>    // for std::to_string

// Function to safely access the element at the given index in an array.
int getElement(const int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of range: " + std::to_string(index));
    }
    return arr[index]; // Return the element at the specified index if the index is valid
}

// Function to set the array element at a given index to a specified value.
void setElement(int* arr, int length, int index, int value) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of range: " + std::to_string(index));
    }
    arr[index] = value; // Set the element at the specified index to the given value
}
