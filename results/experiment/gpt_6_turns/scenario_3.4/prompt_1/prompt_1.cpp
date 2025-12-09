#include <iostream>
#include <stdexcept>

int getElement(int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of range");
    }
    return arr[index];
}

int main() {
    int sampleArray[] = {10, 20, 30, 40, 50};
    int length = sizeof(sampleArray) / sizeof(sampleArray[0]);

    try {
        std::cout << "Element at index 2: " << getElement(sampleArray, length, 2) << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << e.what() << std::endl;
    }

    try {
        std::cout << "Element at index 5: " << getElement(sampleArray, length, 5) << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << e.what() << std::endl;
    }

    return 0;
}
