import logging
from typing import List, Any

logging.basicConfig(level=logging.INFO)  # Increased log level from DEBUG to INFO
logger = logging.getLogger(__name__)

class ArrayManager:
    def __init__(self):
        self.arr: List[Any] = []

    def get_element(self, length: int, index: int) -> Any:
        """
        Returns the element at the given index of an array.

        If the index is out-of-bounds or invalid, raises IndexError with a descriptive message.

        @param length The length of the array.
        @param index The index of the desired element.

        @return The element at the specified index in the array.
        """
        try:
            # Check for integer overflow
            if length > 2**31 - 1 or length < -2**31:  # Added range check
                raise OverflowError("Array size exceeds maximum limit")

            # Check for out-of-bounds access
            if index >= length or index < -length:
                raise IndexError("Index out of bounds")

            return self.arr[index]

        except Exception as e:
            logger.error(f"Failed to retrieve element at index {index}: {str(e)}")
            raise

    def set_element(self, index: int, value: Any) -> None:
        try:
            # Check for integer overflow
            if not isinstance(index, int):
                raise TypeError("Index must be an integer")

            # Check for out-of-bounds access
            if index < -len(self.arr) or index >= len(self.arr):
                raise IndexError("Index out of bounds")

            self.arr[index] = value

        except Exception as e:
            logger.error(f"Failed to set element at index {index}: {str(e)}")
            raise


def create_defensive_copy(array: List[Any]) -> None:
    try:
        # Create a defensive copy using list comprehension
        global array
        array = [element for i, element in enumerate(array) if isinstance(element, (int, float, str))]

    except Exception as e:
        logger.error(f"Failed to create defensive copy: {str(e)}")


def main() -> None:
    try:
        length_str: str = input("Enter the number of elements in the array: ")
        max_indices: int = int(length_str)

        validator = SafeInputValidator()
        if not validator.validate_array_length(max_indices):
            return

        element_values: List[str] = []
        for i in range(max_indices):
            index_str: str = input(f"Enter the index ({i + 1}/%d) of the element: " % max_indices)
            if not validator.validate_index(int(index_str)):
                return
            value = input(f"Enter the element value at index {i + 1}: ")
            try:
                validator.validate_value(value)
                element_values.append(value)
            except ValueError as ve:
                logger.error(f"Failed to validate element value: {ve}")
                return

        array = []
        for i in range(max_indices):
            try:
                array.append(int(element_values[i]))
            except ValueError:
                logger.error("Invalid input. Please enter an integer value.")
                return

        # Create a defensive copy of the array
        create_defensive_copy(array)

        manager = ArrayManager()
        for i in range(max_indices):
            manager.set_element(int(index_str), int(element_values[i]))

        for i in range(max_indices):
            print(manager.get_element(max_indices, i))

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")


class SafeInputValidator:
    def validate_array_length(self, length: int) -> bool:
        return isinstance(length, int)

    def validate_index(self, index: int) -> bool:
        return isinstance(index, int)


if __name__ == "__main__":
    main()
