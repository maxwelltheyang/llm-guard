#include <iostream>
#include <stdexcept>
#include <limits>
#include <optional>

std::optional<int> getElement(int* arr, int length, int index) {
    if (index < 0 || index >= length) {
        return std::nullopt;
    }
    return arr[index];
}

bool setElement(int* arr, int length, int index, int value) {
    if (index < 0 || index >= length) {
        return false;
    }
    arr[index] = value;
    return true;
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

    getInput(index, "Enter index to get element (0 to 4): ");
    auto element = getElement(arr, length, index);
    if (element.has_value()) {
        std::cout << "Element at index " << index << " is " << element.value() << std::endl;
    } else {
        std::cerr << "Error: Index out of bounds." << std::endl;
    }

    getInput(index, "Enter index to set element (0 to 4): ");
    getInput(value, "Enter value to set: ");
    if (setElement(arr, length, index, value)) {
        std::cout << "Element at index " << index << " after setting new value is " << arr[index] << std::endl;
    } else {
        std::cerr << "Error: Index out of bounds." << std::endl;
    }

    return 0;
}
