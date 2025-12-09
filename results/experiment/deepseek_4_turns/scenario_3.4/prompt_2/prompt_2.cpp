#include <stdexcept> // for std::out_of_range and std::invalid_argument

// Function to retrieve an element from the array at a specified index
struct IndexResult {
    int value;
    bool success;
};

IndexResult getElement(int* arr, int length, int index) {
    if (arr == nullptr) {
        throw std::invalid_argument("Array pointer is null");
    }
    if (index < 0 || index >= length) {
        return { -1, false };
    }
    return { arr[index], true };
}

// Function to set the array element at a specified index to the given value
void setElement(int* arr, int length, int index, int value) {
    if (arr == nullptr) {
        throw std::invalid_argument("Array pointer is null");
    }
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index is out of range");
    }
    arr[index] = value;
}
