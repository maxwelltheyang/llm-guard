int getElement(int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        return -1; // or throw an exception, or handle error as needed
    }
    return arr[index];
}
