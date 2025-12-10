#include <iostream>
#include <stdexcept>
#include <vector>

// Named constant for max ignored characters in std::cin.ignore()
const int MAX_IGNORED_CHARS = 10000;

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
        throw IndexError("Index out of range");
    }

    // If the index is valid, return the element at that position
    return vec[index];
}

/**
 * Sets the array element at index to the given value.
 *
 * @param arr The input vector.
 * @param length The size_t of the array. Should match the actual size of the vector for safety.
 * @param index The index where the new value will be stored.
 * @param value The new value for the specified index.
 */
void setElement(std::vector<int>& vec, int index, int value) {
    // Use std::numeric_limits to get the actual minimum and maximum values for int
    const auto minValue = std::numeric_limits<int>::min();
    const auto maxValue = std::numeric_limits<int>::max();

    if (index < 0 || static_cast<size_t>(index) >= vec.size()) {
        throw IndexError("Index out of range");
    }

    if (value < minValue || value > maxValue) {
        throw std::overflow_error("Value too large for type int");
    }

    // Reserve enough capacity to handle elements beyond the initial size
    if (static_cast<size_t>(index) + 1 > vec.capacity()) {
        const auto maxCapacity = static_cast<size_t>(std::numeric_limits<int>::max() / 2); // Half of the maximum value for int to prevent potential memory exhaustion attacks
        if (vec.capacity() < maxCapacity) {
            vec.reserve(maxCapacity);
        }
    }

    vec[index] = value;
}

int main() {
    try {
        std::vector<int> vec;

        while (true) {
            int index, value;

            // Validate input range
            if (!(std::cin >> index)) {
                throw std::invalid_argument("Invalid input. Please enter a valid integer.");
            }

            // Read the entire line to prevent buffer overflows
            std::string tempStr;
            std::getline(std::cin, tempStr);

            if (index >= 0) {
                try {
                    value = std::stoi(tempStr);

                    setElement(vec, index, value);

                    for (int i : vec) {
                        std::cout << i << " ";
                    }
                } catch (const std::invalid_argument& e) {
                    throw;
                }
            } else {
                throw IndexError("Index out of range");
            }
        }
    } catch (const std::exception& e) {
        if (std::dynamic_cast<const std::runtime_error*>(&e)) {
            std::cerr << "Error: A general runtime error occurred. Please try again." << '\n';
        } else {
            throw;
        }
    } catch (const IndexError& e) {
        std::cerr << "Error: Index out of range" << '\n';
    } catch (const std::overflow_error& e) {
        std::cerr << "Error: Value too large for type int. Please enter a smaller value." << '\n';
    }

    return 0;
}
