#include <iostream>
#include <stdexcept>

int getElement(int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of range");
    }
    return arr[index];
}

void setElement(int* arr, int length, int index, int value) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index out of range");
    }
    arr[index] = value;
}

int main() {
    int sampleArray[] = {10, 20, 30, 40, 50};
    int length = sizeof(sampleArray) / sizeof(sampleArray[0]);

    try {
        std::cout << "Element at index 2: " << getElement(sampleArray, length, 2) << std::endl;
        setElement(sampleArray, length, 2, 99);
        std::cout << "Element at index 2 after setting to 99: " << getElement(sampleArray, length, 2) << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << e.what() << std::endl;
    }

    try {
        setElement(sampleArray, length, 5, 100);  // This will throw an exception
    } catch (const std::out_of_range& e) {
        std::cerr << e.what() << std::endl;
    }

    return 0;
}
