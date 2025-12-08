int getElement(int* arr, int length, int index) {
    if (index >= 0 && index < length) {
        return arr[index];
    }
    return -1; // Return an error value if index is out of bounds
}
