#include <stdexcept> // for std::out_of_range

int getElement(int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of bounds");
    }
    return arr[index];
}
