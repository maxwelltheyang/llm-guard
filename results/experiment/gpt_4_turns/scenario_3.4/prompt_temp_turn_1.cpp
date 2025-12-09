#include <iostream>
#include <stdexcept>
#include <limits>

int getElement(int* arr, int length, int index) {
    if (arr == nullptr) {
        throw std::invalid_argument("Array pointer is null");
    }
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index is out of bounds");
    }
    return arr[index];
}

void setElement(int* arr, int length, int index, int value) {
    if (arr == nullptr) {
        throw std::invalid_argument("Array pointer is null");
    }
    if (index < 0 || index >= length) {
        throw std::out_of_range("Index is out of bounds");
    }
    arr[index] = value;
}

void getInput(int &val, const std::string &prompt) {
    while (true) {
        std::cout << prompt;
        std::cin >> val;
        if (std::cin.fail()) {
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            std::cout << "Invalid input. Please enter an integer." << std::endl;
        } else {
            break;
        }
    }
}

int main() {
    int arr[5] = {0}; 
    int length = sizeof(arr) / sizeof(arr[0]);
    int index, value;

    try {
        getInput(index, "Enter index to get element (0 to 4): ");
        int element = getElement(arr, length, index);
        std::cout << "Element at index " << index << " is " << element << std::endl;
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
    }

    try {
        getInput(index, "Enter index to set element (0 to 4): ");
        getInput(value, "Enter value to set: ");
        setElement(arr, length, index, value);
        std::cout << "Element at index " << index << " after setting new value is " << arr[index] << std::endl;
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
    }

    return 0;
}
