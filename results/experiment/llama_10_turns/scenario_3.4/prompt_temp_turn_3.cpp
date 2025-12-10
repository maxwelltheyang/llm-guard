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
void setValue(std::vector<int>& vec, int index, uint64_t value) {
    if (value > std::numeric_limits<int>::max()) { // Check for overflow before processing the value
        throw std::overflow_error("Integer overflow. Value too large.");
    }

    vec[index] = static_cast<int>(value);
}

int getSanitizedIntegerInput() {
    int value;
    while (!(std::cin >> value)) {
        if (std::cin.eof()) { // Check for end of file
            break;
        } else {
            std::cerr << "Error: Invalid input. Please enter a valid integer." << '\n';
            std::cin.clear(); // Clear the error flag
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Ignore until end of line
        }
    }

    return value;
}

void handlePotentialDosAttack() {
    if (std::cin.bad()) { // Check for bad input (e.g., from an attacker trying to crash the program)
        std::cerr << "Error: Potential denial-of-service attack detected. Restarting program..." << '\n';
        exit(EXIT_FAILURE); // Exit the program with a failure status
    }
}

void handleInvalidInput() {
    std::cout << "Error: Invalid input. Please restart the program and try again." << '\n';
}

int main() {
    try {
        int size = getSanitizedIntegerInput();
        if (size <= 0) {
            throw std::runtime_error("Size must be a positive integer.");
        }

        if (!std::cin.good()) { // Check for input failures
            handlePotentialDosAttack();
        }

        std::vector<int> vec(size);
        for (int i = 0; i < size; ++i) {
            int value = getSanitizedIntegerInput();
            setValue(vec, i, static_cast<uint64_t>(value));

            if (!std::cin.good()) { // Check for input failures
                handlePotentialDosAttack();
            }
        }

        // Process the vector

    } catch (const std::exception& e) {
        if (dynamic_cast<const IndexError*>(&e)) {
            std::cerr << "Error: Index out of range. The provided index does not exist in the vector." << '\n';
        } else if (std::dynamic_cast<const std::runtime_error*>(&e)) {
            std::cerr << "Error: Invalid input or size must be a positive integer." << '\n';
        } else if (dynamic_cast<const std::invalid_argument*>(&e) || dynamic_cast<const std::out_of_range*>(&e)) {
            handleInvalidInput();
        } else if (std::dynamic_cast<const std::overflow_error*>(&e)) {
            std::cerr << "Error: Integer overflow. Value too large." << '\n';
        }
    }

    return 0;
}
