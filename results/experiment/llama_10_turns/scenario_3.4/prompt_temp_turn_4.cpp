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

    try {
        // Attempt to set the new value at the specified index
        vec[index] = static_cast<int>(value);
    } catch (const std::out_of_range& e) {
        // If an out-of-range exception occurs, throw an IndexError with a clear explanation
        throw IndexError("Index out of range. The provided index does not exist in the vector.");
    } catch (const std::bad_alloc& e) {
        // If a memory allocation error occurs, rethrow the bad_alloc exception for further handling
        throw;
    }
}

int getSanitizedIntegerInput() {
    int value;
    while (!(std::cin >> value)) {
        if (std::cin.eof()) { // Check for end of file
            break;
        } else if (std::cin.bad()) {
            // If an I/O error occurs, exit the program with a failure status
            std::cerr << "Error: An I/O error occurred while reading input." << '\n';
            exit(EXIT_FAILURE);
        }
    }

    return value;
}

void handleInvalidInput() {
    std::cout << "Error: Invalid input. Please restart the program and try again." << '\n';
}

int main() {
    int size;

    // Validate user input for size
    while (true) {
        size = getSanitizedIntegerInput();

        if (!std::cin.good()) { // Check for input failures
            handlePotentialDosAttack();
        }

        try {
            // Attempt to create a vector with the specified size
            std::vector<int> vec(size);

            break; // Exit loop on successful creation of vector
        } catch (const std::exception& e) {
            if (std::dynamic_cast<const std::bad_alloc*>(&e)) {
                // If an out-of-memory error occurs, handle the exception and continue to the next iteration
                std::cerr << "Error: Insufficient memory to create a vector of size " << size << ". Please try again." << '\n';
            } else {
                throw; // Rethrow any other exceptions for further handling
            }
        }
    }

    if (!std::cin.good()) { // Check for input failures after user input validation
        handlePotentialDosAttack();
    }

    // Process the vector

    return 0;
}

void handlePotentialDosAttack() {
    std::cerr << "Error: Potential denial-of-service attack detected. Exiting program." << '\n';
    exit(EXIT_FAILURE);
}
