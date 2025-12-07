import logging
from typing import List, Any

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ArrayManager:
    def __init__(self):
        self.arr: List[Any] = []

    def get_element(self, length: int, index: int) -> Any:
        """
        Returns the element at the given index of an array.

        If the index is out-of-bounds or invalid, returns None.

        @param length The length of the array.
        @param index The index of the desired element.

        @return The element at the specified index in the array, or None if out-of-range or invalid.
        """
        try:
            # Check for integer overflow
            if length > 2**31 - 1:  # Assuming 32-bit system
                logger.error("Integer overflow: Array size exceeds maximum value")
                return None

            # Directly access the array elements using list indexing (safely handles out-of-range indices)
            if index < 0 or index >= length:
                return None
            return self.arr[index]

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return None

    def set_element(self, index: int, value: Any) -> None:
        """
        Sets a new element at the specified index in the array.

        @param index The index where to set the new value.
        @param value The new value to be assigned.
        """
        try:
            # Check for invalid length
            if not self.arr:
                logger.error("Array is empty")
                return

            # Validate non-negative integer index before setting element
            if not isinstance(index, int):
                logger.error(f"Invalid index type. Expected 'int', got '{type(index)}'.")
                raise TypeError("Index must be an integer.")

            if not 0 <= index < len(self.arr):
                logger.error(f"Out of range index: {index}. Index must be between 0 and {len(self.arr) - 1}.")
                raise IndexError("Index out of range")

            # Try to set the element at the specified index
            try:
                self.arr[index] = value
            except MemoryError as me:
                logger.error(f"Memory error: unable to assign new value due to insufficient memory.")
                raise MemoryError("Insufficient memory to assign a new value")
            except Exception as e:
                logger.error(f"Failed to set element at index {index}: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error in set_element: {str(e)}")


def validate_value(value: Any) -> None:
    try:
        # Attempt to convert the value to an integer (allowing for string inputs)
        int(value)
    except ValueError:
        logger.error("Invalid input. Expected a numeric type, but got '%s'." % str(value))
        raise ValueError("Input must be of type 'int' or convertible to it")


class SafeInputValidator:
    def __init__(self):
        self.max_size: int = 10000

    def validate_array_size(self, size: int) -> bool:
        return 0 <= size <= self.max_size

    def validate_index(self, index: int) -> bool:
        return 0 <= index < self.max_size

    def validate_value(self, value: Any) -> None:
        try:
            validate_value(value)
        except ValueError as ve:
            logger.error(f"Invalid input. {ve}")
            raise


def main() -> None:
    try:
        validator = SafeInputValidator()

        length_str: str = input("Enter the number of elements in the array: ")
        if not validator.validate_array_size(int(length_str)):
            return

        max_indices: int = int(length_str)

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

        manager = ArrayManager()
        for i in range(max_indices):
            manager.set_element(int(index_str), int(element_values[i]))

        for i in range(max_indices):
            print(manager.get_element(max_indices, i))

    except ValueError as ve:
        logger.error(f"Invalid input: {ve}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
