#include <iostream>
#include <stdexcept>
#include <limits>

int getElement(int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index is out of bounds");
    }
    return arr[index];
}

bool setElement(int* arr, int length, int index, int value) {
    if (index < 0 || index >= length) {
        return false; // Return false for out-of-range
    }
    arr[index] = value;
    return true;
}

void clearInputStream(std::istream& in) {
    in.clear(); // Clear cin error flags
    in.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Ignore invalid input
}

int getValidIntegerFromUser() {
    int value;
    while (!(std::cin >> value)) {
        std::cerr << "Invalid input. Please enter an integer: ";
        clearInputStream(std::cin);
    }
    clearInputStream(std::cin);
    return value;
}

int main() {
    int arr[5];
    int length = sizeof(arr) / sizeof(arr[0]); // Calculate array length

    // Initialize array to some default values
    for (int i = 0; i < length; i++) {
        arr[i] = i + 1;
    }

    int index;

    std::cout << "Enter index (0 to 4) to get an element: ";
    index = getValidIntegerFromUser();
    try {
        int element = getElement(arr, length, index);
        std::cout << "Element at index " << index << ": " << element << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << e.what() << std::endl;
    }

    std::cout << "Enter index (0 to 4) to set a value: ";
    index = getValidIntegerFromUser();
    std::cout << "Enter new value: ";
    int value = getValidIntegerFromUser();
    if (setElement(arr, length, index, value)) {
        std::cout << "New element at index " << index << ": " << arr[index] << std::endl;
    } else {
        std::cerr << "Index " << index << " is out of bounds." << std::endl;
    }

    return 0;
}
