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

        return; // Successful operation, no exception thrown
    } catch (const std::exception& e) {
        // Catch specific exceptions that might occur during the assignment and rethrow them for further handling
        if (dynamic_cast<const std::out_of_range*>(&e)) {
            throw IndexError("Index out of range. The provided index does not exist in the vector.");
        } else if (dynamic_cast<const std::bad_alloc*>(&e)) {
            // If a memory allocation error occurs, rethrow it for further handling
            throw;
        } else {
            // Re-throw any other unexpected exceptions for further analysis and handling
            throw;
        }
    }
}

int getSanitizedIntegerInput() {
    int value;

    while (true) {
        std::cout << "Enter a value: ";

        if (!std::cin >> value) {
            if (std::cin.eof()) { // Check for end of file
                std::cerr << "Error: End of file reached." << '\n';
                return INT_MIN; // Return an invalid value to indicate input failure
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

        size = getSanitizedIntegerInput(); // Get a sanitized integer value from the user

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
