#include <iostream>
#include <stdexcept>
#include <vector>

class IndexError : public std::runtime_error {
public:
    IndexError(const std::string& message) : std::runtime_error(message) {}
};

/**
 * Returns the element at the given index of an array, handling out-of-range indices safely.
 *
 * @param arr The input vector.
 * @param index The index of the desired element.
 * @return The element at the specified index if it exists; otherwise, throws an IndexError.
 */
int getElement(const std::vector<int>& vec, int index) {
    try {
        // Attempt to access the element at the given index
        return vec.at(index);

    } catch (const std::out_of_range& e) {
        // If the index is out of range, throw an IndexError with a clear explanation
        throw IndexError("Index out of range. The provided index does not exist in the vector.");
    }
}

/**
 * Sets the array element at index to the given value.
 *
 * @param arr The input vector.
 * @param index The index where the new value will be set.
 * @param value The new value for the specified index in the vector.
 */
void setValue(std::vector<int>& vec, int index, int value) {
    try {
        if (index < 0 || index >= vec.size()) { // Check if the index is within bounds
            throw std::out_of_range("Index out of range");
        }

        vec[index] = value; // Assign the new value to the specified index

        return;
    } catch (const std::exception& e) {
        std::cerr << "Error: Unable to set element at index " << index << ". Reason: " << e.what() << '\n';

        throw; // Rethrow the exception
    }
}

int getSanitizedIntegerInput(const std::string& prompt = "") {
    if (!std::cin.good()) { // Check for input failures before proceeding
        handlePotentialDosAttack();
    }

    int value;

    while (true) {
        if (prompt.empty()) { // If no prompt is provided, display a default message
            std::cout << "Enter an integer value: ";
        } else {
            std::cout << prompt << ": ";
        }

        try {
            value = getIntegerValue(); // Attempt to read and parse the input as an integer

            if (value < INT_MIN || value > INT_MAX) { // If the parsed value is outside the valid range, throw a runtime error
                throw std::runtime_error("Input value is outside the valid range");
            }

            return value; // Return the successfully parsed value
        } catch (const std::exception& e) {
            if (std::cin.eof()) { // Check for end of file
                std::cerr << "Error: End of file reached." << '\n';
            } else if (std::cin.bad() || !std::cin.good()) {
                std::cerr << "I/O error while reading input. Please try again." << '\n';
            } else {
                std::cerr << "Invalid input. Reason: " << e.what() << ". Please try again." << '\n';
            }

            // Clear the input buffer to prevent further errors
            std::cin.clear();
            std::cin.ignore(10000, '\n');
        }
    }
}

int getIntegerValue() {
    int value;

    while (true) {
        if (!(std::cin >> value)) { // Attempt to read and parse the input as an integer
            if (std::cin.eof()) { // Check for end of file
                std::cerr << "Error: End of file reached." << '\n';
            } else if (std::cin.bad() || !std::cin.good()) {
                std::cerr << "I/O error while reading input. Please try again." << '\n';
            } else {
                std::cerr << "Invalid input. Please enter a valid integer value." << '\n';
            }

            // Clear the input buffer to prevent further errors
            std::cin.clear();
            std::cin.ignore(10000, '\n');
        } else {
            return value; // Return the successfully parsed value
        }
    }
}

int main() {
    if (!std::cin.good()) { // Check for input failures before proceeding
        handlePotentialDosAttack();
    }

    int size;

    while (true) {
        std::cout << "Enter the size of the vector: ";

        size = getSanitizedIntegerInput("Size"); // Get a sanitized integer value from the user

        if (size < 0) { // If an invalid value was returned due to input failure, exit the loop
            break;
        }

        try {
            std::vector<int> vec(size); // Attempt to create a vector of the specified size

            if (!std::cin.good()) { // Check for input failures after user input validation
                handlePotentialDosAttack();
            } else {
                // Process the vector

                return 0;
            }
        } catch (const std::exception& e) {
            if (dynamic_cast<const std::bad_alloc*>(&e)) {
                std::cerr << "Error: Insufficient memory to create a vector of size " << size << ". Please try again." << '\n';
            } else {
                throw; // Rethrow any other exceptions for further handling
            }
        }
    }

    return 0;
}

void handlePotentialDosAttack() {
    std::cerr << "Error: Potential denial-of-service attack detected. Exiting program." << '\n';
    exit(EXIT_FAILURE);
}
