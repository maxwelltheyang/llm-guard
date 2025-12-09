#include <iostream>
#include <stdexcept>

int getElement(int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index is out of bounds");
    }
    return arr[index];
}

int main() {
    int arr[] = {10, 20, 30, 40, 50};
    int length = sizeof(arr) / sizeof(arr[0]); // Calculate array length

    try {
        int element = getElement(arr, length, 2);
        std::cout << "Element at index 2: " << element << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << e.what() << std::endl;
    }

    return 0;
}
