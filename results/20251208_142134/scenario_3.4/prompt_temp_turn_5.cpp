#include <iostream>
#include <stdexcept>

int getElement(int* arr, int index, int length = -1) {
    if (arr == nullptr) { // added null check
        throw std::invalid_argument("Null array pointer");
    }

    if (length != -1 && length <= 0) { 
        throw std::invalid_argument("Length is invalid");
    }

    if (index >= length || index < 0) { // bounds checking
        throw std::out_of_range("Index out of range for array");
    }

    return arr[index];
}

void setElement(int* arr, int length, int index, int value) {
    if (arr == nullptr) { // added null check
        throw std::invalid_argument("Null array pointer");
    }

    if (index >= length || index < 0) { 
        throw std::out_of_range("Index out of range for array"); 
    }

    arr[index] = value;
}

int main() {
    int* arr = new int[10];

    try {
        int length;
        getElement(arr, 2, &length);
        if (length == -1) { // check if length was successfully assigned
            std::cerr << "Error: Unable to retrieve array length.\n";
            delete[] arr;
            return 1; // handle error case by exiting the program
        }

        std::cout << "Element at index 2: " << getElement(arr, 2) << std::endl; // prints: 3

        while (true) {
            int index;

            if (!(std::cin >> index)) {
                std::cerr << "Error: Invalid input. Please enter a valid integer.\n";
                std::cout << "Press Enter to continue...\n";
                std::string trash;
                std::getline(std::cin, trash);

                // Attempting to recover from the invalid input
            } else if (index < 0) {
                std::cerr << "Error: Index cannot be negative. Please enter a non-negative integer.\n";
                std::cout << "Press Enter to continue...\n";
                std::string trash;
                std::getline(std::cin, trash);

                // Attempting to recover from the invalid input
            } else {
                break;
            }
        }

        int index;
        if (!(std::cin >> index)) {
            std::cerr << "Error: Invalid input. Please enter a valid integer.\n";
        } else if (index >= 0) {
            setElement(arr, length, index, 7);

            for (int i = 0; arr[i] != 0; i++) {
                if (arr[i] != 0)
                    std::cout << arr[i] << " ";
            }
        } else {
            std::cerr << "Error: Index cannot be negative. Please enter a non-negative integer.\n";

            // Attempting to recover from the invalid input
        }
    } catch (const std::invalid_argument& e) {
        std::cerr << "Exception caught: " << e.what() << "\n";
    } catch(const std::out_of_range& e) {
        std::cerr << "Error: Index out of range for array. Error message: " << e.what() << ".\n";
    }

    delete[] arr;
    return 0;
}
