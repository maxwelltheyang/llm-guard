int getElement(int* arr, int length, int index) {
    if (index >= 0 && index < length) {
        return arr[index];
    } else {
        throw std::out_of_range("Index out of bounds");
    }
}
