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

int main() {
    try {
        // Read input values and store them in a vector
        std::vector<int> vec;

        while (true) {
            int value;

            if (std::cin >> value) {
                try {
                    setValue(vec, 0, static_cast<uint64_t>(value));

                    // Handle out-of-range indices safely when accessing elements
                    for (int i = 1; i < vec.size(); ++i) {
                        std::cout << "Value at index " << i << ": " << getElement(vec, i) << "\n";
                    }
                } catch (const std::invalid_argument& e) {
                    std::cerr << "Error: Invalid input. Please enter a valid integer." << '\n';
                } catch (const std::overflow_error& e) {
                    std::cerr << "Error: Integer overflow. Value too large." << '\n';
                }
            } else if (std::cin.eof()) { // Check for end of file
                break;
            } else {
                throw std::runtime_error("Failed to read input value");
            }
        }

    } catch (const std::exception& e) {
        if (dynamic_cast<const IndexError*>(&e)) {
            std::cerr << "Error: Index out of range. The provided index does not exist in the vector." << '\n';
        } else if (std::dynamic_cast<const std::runtime_error*>(&e)) {
            std::cerr << "Error: Failed to read input value" << '\n';
        } else if (dynamic_cast<const std::invalid_argument*>(&e)) {
            std::cerr << "Error: Invalid input. Please enter a valid integer." << '\n';
        } else if (std::dynamic_cast<const std::overflow_error*>(&e)) {
            std::cerr << "Error: Integer overflow. Value too large." << '\n';
        }
    }

    return 0;
}
