import logging
from typing import List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArrayManager:
    def __init__(self):
        self.arr: List[Any] = []

    def get_element(self, length: int, index: int) -> Any:
        try:
            # Check for integer overflow
            if length > 2**31 - 1 or length < -2**31:
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


def create_defensive_copy(array: List[Any]) -> List[Any]:
    try:
        # Create a deep copy using the deepcopy function from the copy module
        import copy
        return copy.deepcopy(array)

    except Exception as e:
        logger.error(f"Failed to create defensive copy: {str(e)}")
        raise


class SafeInputValidator:
    def validate_array_length(self, length: int) -> bool:
        return isinstance(length, int)

    def validate_index(self, index: int) -> bool:
        return isinstance(index, int)


def validate_value(value: str) -> None:
    try:
        # Attempt to convert the value to an integer
        int(value)
    except ValueError as ve:
        logger.error(f"Failed to validate element value: {ve}")
        raise


def main():
    array_manager = ArrayManager()

    max_indices_str = input("Enter the maximum number of indices (integer): ")

    if not SafeInputValidator().validate_array_length(int(max_indices_str)):
        print("Invalid input. Please enter a valid integer value.")
        exit(1)

    element_values = []

    for i in range(int(max_indices_str)):
        index_str = input(f"Enter the index ({i + 1}/{max_indices_str}) of the element: ")

        if not SafeInputValidator().validate_index(int(index_str)):
            print("Invalid index. Please enter a valid integer value.")
            exit(1)

        value = input(f"Enter the element value at index {i + 1}: ")

        try:
            validate_value(value)
            element_values.append(int(value))
        except ValueError as ve:
            logger.error(f"Failed to validate element value: {ve}")
            print("Invalid input. Please enter a valid integer value.")
            exit(1)

    # Create a defensive copy of the array
    defensive_copy = create_defensive_copy(element_values)

    for i in range(len(defensive_copy)):
        array_manager.set_element(int(index_str), defensive_copy[i])

    for i in range(len(defensive_copy)):
        print(array_manager.get_element(len(defensive_copy), i))


if __name__ == "__main__":
    main()
