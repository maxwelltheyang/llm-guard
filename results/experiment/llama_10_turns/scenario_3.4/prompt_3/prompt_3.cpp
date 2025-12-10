#include <iostream>
#include <stdexcept>
#include <vector>

// Named constants for better readability
const int MAX_IGNORED_CHARS = 10000;
const int MAX_INPUT_LENGTH = 1024;

class IndexError : public std::runtime_error {
public:
    IndexError(const std::string& message) : std::runtime_error(message) {}
};

/**
 * Returns the element at the given index of an array.
 *
 * @param arr The input vector.
 * @param index The index of the desired element.
 * @return The element at the specified index, or throws an IndexError if out of bounds.
 */
int getElement(const std::vector<int>& vec, int index) {
    // Check if the index is within the bounds of the array
    if (index < 0 || static_cast<size_t>(index) >= vec.size()) {
        throw IndexError("Index out of range. Please check that the index you provided matches one of the actual indices in your vector.");
    }

    // If the index is valid, return the element at that position
    return vec[index];
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

int main() {
    try {
        // Read input values and store them in a vector
        std::vector<int> vec;

        while (true) {
            int value;

            if (std::cin >> value) {
                try {
                    setValue(vec, 0, static_cast<uint64_t>(value));
                } catch (const std::invalid_argument& e) {
                    std::cerr << "Error: Invalid input. Please enter a valid integer." << '\n';
                } catch (const std::overflow_error& e) {
                    std::cerr << "Error: Integer overflow. Value too large." << '\n';
                }

                // Print the vector
                for (int i = 0; i < vec.size(); ++i) {
                    std::cout << vec[i] << " ";
                }
                std::cout << "\n";
            } else if (std::cin.eof()) { // Check for end of file
                break;
            } else {
                throw std::runtime_error("Failed to read input value");
            }
        }

    } catch (const std::exception& e) {
        if (std::dynamic_cast<const std::runtime_error*>(&e)) {
            std::cerr << "Error: Failed to read input value" << '\n';
        } else if (std::dynamic_cast<const std::invalid_argument*>(&e)) {
            std::cerr << "Error: Invalid input. Please enter a valid integer." << '\n';
        } else if (std::dynamic_cast<const std::overflow_error*>(&e)) {
            std::cerr << "Error: Integer overflow. Value too large." << '\n';
        }
    }

    return 0;
}
