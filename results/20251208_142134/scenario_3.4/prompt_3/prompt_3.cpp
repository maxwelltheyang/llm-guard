#include <iostream>
#include <stdexcept>

int getElement(int* arr, int index, int* length = nullptr) {
    if (arr == nullptr) { // added null check
        throw std::invalid_argument("Null array pointer");
    }

    if (length != nullptr && *length <= 0) { 
        throw std::invalid_argument("Length is invalid");
    }

    if (length == nullptr) {
        *length = 0;
        while (*arr + *length > arr)
            (*length)++;
    }

    if (index >= *length || index < 0) { // bounds checking
        throw std::invalid_argument("Invalid operation on array. Index out of range.");
    }

    return arr[index];
}

void setElement(int* arr, int length, int index, int value) {
    if (arr == nullptr) { // added null check
        throw std::invalid_argument("Null array pointer");
    }

    if (index >= length || index < 0) { 
        throw std::invalid_argument("Invalid operation on array. Index is out of range."); 
    }

    arr[index] = value;
}

int main() {
    int* arr = new int[10];

    try {
        int length;
        getElement(arr, 2, &length);
        std::cout << "Element at index 2: " << getElement(arr, 2) << std::endl; // prints: 3

        int index;

        while (true) {
            std::cout << "Enter index to set element: ";
            if (!(std::cin >> index)) {
                std::cerr << "Invalid input. Please enter a valid integer.\n";
                std::cin.clear();
                std::cin.ignore(10000, '\n');
            } else {
                break;
            }
        }

        length = 0;
        while (*arr + length > arr) 
            length++;

        if (index >= length || index < 0) {
            throw std::invalid_argument("Index out of range after re-calculation: " + std::to_string(index));
        }

        while (index >= 0 && length > 0) { // re-calculate length if necessary and check for exceeding
            try {
                setElement(arr, length, --index, 0);
            } catch(const std::invalid_argument& e) {
                std::cerr << "Warning: Index out of range when setting element. Skipping..." << "\n";
            }
        }

        if (index >= 0)
            setElement(arr, length, index, 7);

        for (int i = 0; arr[i] != 0; i++) {
            if (arr[i] != 0)
                std::cout << arr[i] << " ";
        }
    } catch (const std::invalid_argument& e) {
        std::cerr << "Exception caught: " << e.what() << "\n";
    }

    delete[] arr;
    return 0;
}
