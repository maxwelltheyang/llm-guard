#include <stdexcept> // for std::out_of_range

// Function to retrieve an element from the array at a specified index
int getElement(int* arr, int length, int index) {
    if (arr == nullptr) {
        throw std::invalid_argument("Array pointer is null");
    }

    // Range check and return default value for invalid index
    if (index < 0 || index >= length) {
        return -1; // Return a default value indicating an error
    }
    return arr[index];
}
